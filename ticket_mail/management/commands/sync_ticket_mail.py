import base64
import mimetypes
import re
from datetime import datetime, timedelta
from datetime import timezone as datetime_timezone
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parseaddr
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.html import strip_tags
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from ticket_mail.models import (
    AllowedEmailDomain,
    MailboxSyncState,
    SupportTicket,
    TicketAttachment,
    TicketEmailMessage,
)

MAILBOX = "ticket@thedeepseafood.com"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
SCAN_OVERLAP = timedelta(hours=24)


def decode_gmail_raw(value):
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded)


def extract_body(message):
    """Get readable text, preferring the email's plain-text part."""
    part = message.get_body(preferencelist=("plain", "html"))
    if part is None:
        return ""

    content = part.get_content()
    if part.get_content_type() == "text/html":
        return strip_tags(content).strip()

    return str(content).strip()


def extract_html_body(message):
    """Keep the HTML for the protected original-email preview."""
    part = message.get_body(preferencelist=("html",))
    if part is None:
        return ""
    return str(part.get_content())


def extract_request_text(body):
    """Keep the request above a standard '--' email signature."""
    text = body.replace("\r\n", "\n").strip()
    signature = re.search(r"(?m)^\s*--\s*$", text)

    if signature:
        text = text[: signature.start()].strip()

    return text


def is_addressed_to_mailbox(message):
    header_values = []
    for name in ("To", "Cc", "Delivered-To", "X-Original-To"):
        header_values.extend(message.get_all(name, []))

    recipients = {address.strip().lower() for _, address in getaddresses(header_values)}
    return MAILBOX in recipients


def is_automated(message):
    auto_submitted = str(message.get("Auto-Submitted", "")).lower()
    precedence = str(message.get("Precedence", "")).lower()

    return (
        auto_submitted not in ("", "no")
        or precedence in ("bulk", "junk", "list")
        or message.get("List-Id") is not None
    )


def sender_is_allowed(sender_email):
    if "@" not in sender_email:
        return False

    domain = sender_email.rsplit("@", 1)[1].lower().rstrip(".")
    return AllowedEmailDomain.objects.filter(
        domain=domain,
        is_active=True,
    ).exists()


def save_attachments(parsed_message, ticket, ticket_message):
    """Save normal attachments and CID images used inside email HTML."""
    count = 0

    for index, part in enumerate(parsed_message.walk()):
        if part.is_multipart():
            continue

        content_id = str(part.get("Content-ID", "")).strip().strip("<>")
        filename = part.get_filename()
        is_inline_image = bool(content_id) and part.get_content_maintype() == "image"

        if not filename and not is_inline_image:
            continue

        content = part.get_payload(decode=True)
        if content is None:
            continue

        if filename:
            safe_name = filename.replace("\\", "/").split("/")[-1][:255]
        else:
            extension = mimetypes.guess_extension(part.get_content_type()) or ""
            safe_name = f"inline-image-{index}{extension}"

        if not safe_name:
            continue

        attachment = TicketAttachment(
            ticket=ticket,
            message=ticket_message,
            part_index=index,
            original_name=safe_name,
            content_type=part.get_content_type(),
            content_id=content_id[:255],
            is_inline=(part.get_content_disposition() == "inline" or bool(content_id)),
            size=len(content),
        )
        attachment.file.save(
            safe_name,
            ContentFile(content),
            save=False,
        )
        attachment.save()
        count += 1

    return count


class Command(BaseCommand):
    help = "Import ticket emails and send confirmations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--initialize",
            action="store_true",
            help="Start importing from now without importing older mail",
        )

    def handle(self, *args, **options):
        if options["initialize"]:
            state, created = MailboxSyncState.objects.get_or_create(pk=1)

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Mailbox import starts from {state.started_at}")
                )
            else:
                self.stdout.write(
                    f"Already initialized from {state.started_at}; "
                    "start time unchanged."
                )
            return

        try:
            state = MailboxSyncState.objects.get(pk=1)
        except MailboxSyncState.DoesNotExist as exc:
            raise CommandError("Run sync_ticket_mail --initialize first.") from exc

        if not AllowedEmailDomain.objects.filter(is_active=True).exists():
            raise CommandError("Add active Allowed Email Domains in admin first.")

        token_path = Path(settings.GOOGLE_TICKET_TOKEN_FILE)
        if not token_path.is_file():
            raise CommandError(
                "Mailbox token not found. Connect the Google mailbox first."
            )

        # Set the next cursor only after the entire import succeeds.
        scan_started_at = timezone.now()

        scan_from = state.started_at
        if state.last_checked_at is not None:
            scan_from = max(
                state.started_at,
                state.last_checked_at - SCAN_OVERLAP,
            )

        credentials = Credentials.from_authorized_user_file(
            str(token_path),
            SCOPES,
        )
        service = build("gmail", "v1", credentials=credentials)

        query = f"after:{int(scan_from.timestamp())}"
        gmail_ids = []
        page_token = None

        while True:
            result = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    labelIds=["INBOX"],
                    q=query,
                    maxResults=100,
                    pageToken=page_token,
                )
                .execute()
            )
            gmail_ids.extend(item["id"] for item in result.get("messages", []))

            page_token = result.get("nextPageToken")
            if not page_token:
                break

        # Fetch and sort by received time so an original email is
        # imported before later messages in the same Gmail thread.
        messages = []

        for gmail_id in dict.fromkeys(gmail_ids):
            if TicketEmailMessage.objects.filter(gmail_message_id=gmail_id).exists():
                continue

            data = (
                service.users()
                .messages()
                .get(userId="me", id=gmail_id, format="raw")
                .execute()
            )
            messages.append(data)

        messages.sort(key=lambda item: int(item["internalDate"]))

        created_count = 0
        reply_count = 0
        attachment_count = 0
        skipped_count = 0

        for data in messages:
            gmail_id = data["id"]
            received_at = datetime.fromtimestamp(
                int(data["internalDate"]) / 1000,
                tz=datetime_timezone.utc,
            )

            if received_at <= state.started_at:
                skipped_count += 1
                continue

            parsed = BytesParser(policy=policy.default).parsebytes(
                decode_gmail_raw(data["raw"])
            )

            if not is_addressed_to_mailbox(parsed) or is_automated(parsed):
                skipped_count += 1
                continue

            sender_name, sender_email = parseaddr(str(parsed.get("From", "")))
            sender_email = sender_email.strip().lower()

            if sender_email == MAILBOX or not sender_is_allowed(sender_email):
                skipped_count += 1
                continue

            subject = str(parsed.get("Subject", "")).strip()[:255]
            subject = subject or "(No subject)"

            body = extract_body(parsed)
            html_body = extract_html_body(parsed)
            request_text = extract_request_text(body)
            thread_id = data["threadId"]

            with transaction.atomic():
                earlier_message = (
                    TicketEmailMessage.objects.select_related("ticket")
                    .filter(gmail_thread_id=thread_id)
                    .order_by("received_at")
                    .first()
                )

                if earlier_message:
                    ticket = earlier_message.ticket
                    is_reply = True
                else:
                    ticket = SupportTicket.objects.create(
                        subject=subject,
                        requester_name=sender_name[:255],
                        requester_email=sender_email,
                        description=request_text or "(No text body)",
                        received_at=received_at,
                    )
                    is_reply = False

                ticket_message = TicketEmailMessage.objects.create(
                    ticket=ticket,
                    gmail_message_id=gmail_id,
                    gmail_thread_id=thread_id,
                    sender_email=sender_email,
                    subject=subject,
                    body=body,
                    html_body=html_body,
                    received_at=received_at,
                )

                saved_files = save_attachments(
                    parsed,
                    ticket,
                    ticket_message,
                )

            if is_reply:
                reply_count += 1
            else:
                created_count += 1

            attachment_count += saved_files

        # Retry acknowledgments that failed on an earlier run.
        pending = SupportTicket.objects.filter(
            confirmation_sent_at__isnull=True,
            email_messages__isnull=False,
        ).distinct()

        for ticket in pending:
            try:
                sent = send_mail(
                    subject=f"[{ticket.ticket_number}] Request received",
                    message=(
                        f"Hello {ticket.requester_name or 'there'},\n\n"
                        "We have received your IT support request.\n\n"
                        f"Ticket number: {ticket.ticket_number}\n"
                        f"Subject: {ticket.subject}\n\n"
                        "Our team will review it and get back to you.\n\n"
                        "IT Support Team"
                    ),
                    from_email=MAILBOX,
                    recipient_list=[ticket.requester_email],
                    fail_silently=False,
                )

                if sent != 1:
                    raise RuntimeError("Email backend did not report a sent message")
            except Exception as exc:
                self.stderr.write(
                    f"Confirmation failed for " f"{ticket.ticket_number}: {exc}"
                )
                continue

            ticket.confirmation_sent_at = timezone.now()
            ticket.save(update_fields=["confirmation_sent_at"])

        state.last_checked_at = scan_started_at
        state.save(update_fields=["last_checked_at"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} ticket(s); "
                f"attached {reply_count} reply/replies; "
                f"saved {attachment_count} attachment(s); "
                f"skipped {skipped_count} message(s)."
            )
        )
