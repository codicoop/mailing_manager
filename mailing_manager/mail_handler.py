from collections import Iterable
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email

from .mail_template import MailTemplate


class MailHandler(MailTemplate):
    from_address = None
    to = None
    cc = None
    bcc = None
    debug_bcc = None

    def __init__(self, text_identifier):
        super(MailHandler, self).__init__(text_identifier)
        if hasattr(settings, 'MAILING_MANAGER_DEFAULT_FROM'):
            self.from_address = settings.MAILING_MANAGER_DEFAULT_FROM

    def send(self):
        self._validate_values()
        mail_object = self._setup_email()
        self._send(mail_object)

    @staticmethod
    def _send(mail_object):
        """
        :param mail_object: EmailMultiAlternatives object ready to be sent.
        :return: Nothing
        """
        mail_object.send()

    def _validate_values(self):
        if not isinstance(self.to, str) and not isinstance(self.to, Iterable):
            raise TypeError(
                "TemplateMail.to should be a string or an iterable.")

        if not isinstance(self.from_address, str):
            raise TypeError("TemplateMail.from_address needs to be a string.")

        validate_email(self.from_address)

    def _setup_email(self):
        msg = EmailMultiAlternatives(
            self.get_rendered_subject(),
            self.get_plain_text_body(),
            self.from_address,
            self._normalize_to_iterable(self.to))
        if self.cc:
            msg.cc = self._normalize_to_iterable(self.cc)
        full_bcc = self._get_bcc_with_debugging_copy()
        if full_bcc:
            msg.bcc = self._normalize_to_iterable(full_bcc)
        msg.attach_alternative(self.get_rendered_html_body(), "text/html")
        return msg

    def _get_bcc_with_debugging_copy(self):
        iterable_bcc = []
        if isinstance(self.bcc, str):
            iterable_bcc.append(self.bcc)
        elif isinstance(self.bcc, Iterable):
            iterable_bcc.extend(self.bcc)

        if hasattr(settings, 'DEBUG') and settings.DEBUG is True:
            if isinstance(self.debug_bcc, str):
                iterable_bcc.append(self.debug_bcc)
            elif isinstance(self.debug_bcc, Iterable):
                iterable_bcc.extend(self.debug_bcc)

        return iterable_bcc

    @staticmethod
    def _normalize_to_iterable(string_or_iterable):
        if isinstance(string_or_iterable, str):
            return [string_or_iterable, ]
        elif isinstance(string_or_iterable, Iterable):
            return string_or_iterable
        else:
            raise TypeError(
                f"Value '{str(string_or_iterable)} should be a string or an "
                f"iterable.")
