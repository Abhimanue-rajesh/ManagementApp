from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class Command(BaseCommand):
    help = "Check the connection and show the latest ticket mailbox emails"

    def handle(self, *args, **options):
        try:
            credentials = Credentials.from_authorized_user_file(
                settings.GOOGLE_TICKET_TOKEN_FILE,
                SCOPES,
            )
            service = build("gmail", "v1", credentials=credentials)

            profile = service.users().getProfile(userId="me").execute()
            email = profile["emailAddress"].lower()
            if email != "ticket@thedeepseafood.com":
                raise CommandError(f"Wrong mailbox connected: {email}")

            result = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    labelIds=["INBOX"],
                    maxResults=5,
                )
                .execute()
            )

            self.stdout.write(f"Connected mailbox: {email}")
            for item in result.get("messages", []):
                message = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=item["id"],
                        format="metadata",
                        metadataHeaders=["From", "Subject", "Date"],
                    )
                    .execute()
                )
                headers = {
                    header["name"].lower(): header["value"]
                    for header in message["payload"].get("headers", [])
                }
                self.stdout.write(
                    f'{item["id"]} | {headers.get("from", "")} | '
                    f'{headers.get("subject", "")}'
                )

        except FileNotFoundError as exc:
            raise CommandError(
                "Mailbox token not found. Complete browser authorization first."
            ) from exc
