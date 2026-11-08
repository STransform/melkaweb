import threading
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


class ThreadEmailSender(threading.Thread):
    """ Sends emails dynamically using a thread. """

    def __init__(self, template, subject, to_email, params=None, sender_name=None):
        super().__init__()
        self.template = template
        self.subject = subject
        self.to_email = to_email
        self.params = params or {}
        self.sender_name = sender_name or "OTech Engineering"
        self.attachments = []  # List to store attachments
        self.result_event = threading.Event()

    def run(self):
        try:
            mail_subject = self.subject
            message = render_to_string(self.template, self.params)
            email_from = getattr(settings, "DEFAULT_FROM_EMAIL", self.sender_name)
            email = EmailMultiAlternatives(mail_subject, message, email_from, [self.to_email], )

            for attachment in self.attachments:
                email.attach(*attachment)

            email.attach_alternative(message, 'text/html')
            email.send(fail_silently=False)
            print(f"Sent activation email to {self.to_email}")
            self.result_event.set()
        except Exception as e:
            print(f'Failed to send email to {self.to_email}: {e}')
            self.result_event.set()

    def update_params(self, new_params):
        """
        Update email parameters dynamically.
        :param new_params: A dictionary of new parameters to update.
        """
        self.params.update(new_params)

    def add_attachment(self, file_path, content_type=None, filename=None):
        """
        Add an attachment to the email.
        :param file_path: The path to the file to be attached.
        :param content_type: The MIME type of the attachment.
        :param filename: The filename to be used for the attachment.
        """
        self.attachments.append((file_path, content_type, filename))
