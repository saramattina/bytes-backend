"""
Custom Django email backend for SendGrid API
This bypasses SMTP which may be blocked on Railway
"""
import os
from django.core.mail.backends.base import BaseEmailBackend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content


class SendGridBackend(BaseEmailBackend):
    """
    Email backend that uses SendGrid's API instead of SMTP
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("SENDGRID_API_KEY environment variable is required")

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of successfully sent messages.
        """
        if not email_messages:
            return 0

        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("SENDGRID_API_KEY is not set")
            return 0

        sg = SendGridAPIClient(self.api_key)
        num_sent = 0

        for message in email_messages:
            try:
                # Create SendGrid Mail object
                from_email = Email(message.from_email)
                to_emails = [To(email) for email in message.to]

                # Handle both plain text and HTML content
                if message.content_subtype == 'html':
                    content = Content("text/html", message.body)
                else:
                    content = Content("text/plain", message.body)

                # Create the mail object
                mail = Mail(
                    from_email=from_email,
                    to_emails=to_emails,
                    subject=message.subject,
                    plain_text_content=message.body if message.content_subtype == 'plain' else None,
                    html_content=message.body if message.content_subtype == 'html' else None
                )

                # Send the email
                response = sg.send(mail)

                if response.status_code >= 200 and response.status_code < 300:
                    num_sent += 1
                elif not self.fail_silently:
                    raise Exception(f"SendGrid API error: {response.status_code} - {response.body}")

            except Exception as e:
                if not self.fail_silently:
                    raise

        return num_sent
