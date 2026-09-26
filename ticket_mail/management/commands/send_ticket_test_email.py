# from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Send a test email from the ticket mailbox"

    def handle(self, *args, **options):
        recipient = "abhimanue@thedeepseafood.com"
        sender = "ticket@thedeepseafood.com"

        try:
            sent = send_mail(
                subject="Ticket System – Email Test",
                message=(
                    "This is a test email from the IT ticketing system.\n\n"
                    "The outgoing email configuration is working."
                ),
                from_email=sender,
                recipient_list=[recipient],
                fail_silently=False,
            )
        except Exception as exc:
            raise CommandError(f"Test email failed: {exc}") from exc

        if sent != 1:
            raise CommandError("Django did not report the email as sent.")

        self.stdout.write(self.style.SUCCESS(f"Test email sent to {recipient}"))
