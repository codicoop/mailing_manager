from collections import Iterable
from mailqueue.models import MailerMessage

from .mail_handler import MailHandler


class MailQueueHandler(MailHandler):
    prune_older_than = 30
    now = False

    def send(self, now=False):
        """
        Adding 'now' and auto-pruning functionality.
        :param now: In case you are using a mail_handler like mail_queue, you
        might want the option to send it immediately instead of queuing it.
        :return: Nothing
        """
        self.now = now
        super().send()
        self.prune_old_mails()

    def prune_old_mails(self):
        """
        Wrapper for mail_queue's function for clearing old log entries.
        Beware that only deletes already sent e-mails.

        :return: Nothing
        """
        if isinstance(self.prune_older_than, int):
            # mail_queue expects the offset in hours.
            offset = self.prune_older_than * 24
            MailerMessage.objects.clear_sent_messages(offset)

    def _send(self, mail_object):
        """
        :param mail_object: In this case is a mail_queue object, so doing a
        .save() adds it to sending queue.
        :return: Nothing
        """
        mail_object.save()
        if self.now:
            mail_object.send_mail()

    def _setup_email(self):
        msg = MailerMessage()
        msg.from_address = self.from_address
        msg.to_address = self._get_formatted_recipients(self.to)
        if self.cc:
            msg.cc_address = self._get_formatted_recipients(self.cc)
        full_bcc = self._get_bcc_with_debugging_copy()
        if full_bcc:
            msg.bcc_address = self._get_formatted_recipients(full_bcc)
        msg.subject = self.get_rendered_subject()
        msg.html_content = self.get_rendered_html_body()
        msg.content = self.get_plain_text_body()
        msg.app = self.mail.text_identifier
        return msg

    @staticmethod
    def _get_formatted_recipients(addresses):
        """
        Mail Queue needs it to be a string, instead of a list or tuple like
        EmailMultiAlternatives.
        :param addresses: string or iterable containing e-mails.
        :return: String with all the e-mails separated by comma.
        """
        if isinstance(addresses, str):
            return addresses
        if isinstance(addresses, Iterable):
            return ', '.join(addresses)
        return None
