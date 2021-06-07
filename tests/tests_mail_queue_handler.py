import datetime

from django.test import TestCase
from django.utils import timezone
from mailqueue.models import MailerMessage

from mailing_manager.mail_queue_handler import MailQueueHandler
from .factories.mail import MailFactory


class MailQueueHandlerTest(TestCase):

    def templatemail_send(self, now=False):
        MailFactory()
        mailhandler = MailQueueHandler('IDENTIFIER')
        mailhandler.from_address = "from@example.com"
        mailhandler.body_strings = {'body_string_1': 'first body string',
                                    'body_string_2': 'second body string', }
        mailhandler.subject_strings = {'subject_string_1': 'first string',
                                       'subject_string_2': 'second string', }
        mailhandler.to = "a@example.com"
        mailhandler.cc = "b@example.com"
        mailhandler.bcc = ("c@example.com", "d@example.com",)
        mailhandler.send(now)

    # send()
    def test_templatemail_send(self):
        self.templatemail_send()

        # As this send() doesn't send anything but stores it in a model, we
        # directly check mail_queue model:
        queued_mail = MailerMessage.objects.get(app='IDENTIFIER')
        self.assertFalse(queued_mail.sent)
        self.assertEqual(
            queued_mail.subject, "Subject first string and second string")
        self.assertEqual(
            queued_mail.content,
            "Body: first body string and second body string"
        )
        self.assertEqual(queued_mail.app, 'IDENTIFIER')
        self.assertEqual(queued_mail.to_address, "a@example.com")
        self.assertEqual(queued_mail.cc_address, "b@example.com")
        self.assertEqual(
            queued_mail.bcc_address, "c@example.com, d@example.com")
        self.assertEqual(queued_mail.from_address, "from@example.com")

    def create_mail_queue_old_sent_mail(self, days=31):
        old_date = timezone.now() - datetime.timedelta(days=days)
        MailerMessage.objects.create(
            created=old_date,
            subject='Old mail subject',
            sent=True,
            last_attempt=old_date
        )

    # prune_old_mails()
    def test_prune_old_mails(self):
        self.create_mail_queue_old_sent_mail()
        created = MailerMessage.objects.get(subject='Old mail subject')
        self.assertTrue(isinstance(created, MailerMessage))
        self.templatemail_send()

        # Default pruning antiquity is 30 days, this is 31 days old. After
        # send(), should not exist:
        with self.assertRaises(MailerMessage.DoesNotExist):
            created = MailerMessage.objects.get(subject='Old mail subject')

        self.create_mail_queue_old_sent_mail(29)
        self.templatemail_send()
        created = MailerMessage.objects.get(subject='Old mail subject')
        # Default pruning antiquity is 30 days, this is 29 days old. After
        # send(), should still be there:
        self.assertTrue(isinstance(created, MailerMessage))

    # _send()
    def test__send(self):
        """
        Normal send() is already tested, here only adding the now=True way.
        """
        self.templatemail_send(True)
        queued_mail = MailerMessage.objects.get(app='IDENTIFIER')
        self.assertTrue(queued_mail.sent)

    # _setup_email()
    def test__setup_email(self):
        # I guess coverage is not missing it because it's tested when testing
        # send()?
        pass

    # _get_formatted_recipients()
    def test_get_formatted_recipients(self):
        MailFactory()
        mailhandler = MailQueueHandler('IDENTIFIER')
        recipients = ("a@example.com", "b@example.com", )
        self.assertEqual(
            mailhandler._get_formatted_recipients(recipients),
            "a@example.com, b@example.com"
        )

        self.assertEqual(
            mailhandler._get_formatted_recipients("singlestring@example.com"),
            "singlestring@example.com"
        )

        self.assertTrue(mailhandler._get_formatted_recipients(12) is None)
