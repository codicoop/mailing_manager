from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core import mail

from .factories.mail import MailFactory
from ..mail_handler import MailHandler


class MailHandlerTest(TestCase):

    # __init__()
    def test___init__(self):
        MailFactory()
        with self.settings(MAILING_MANAGER_DEFAULT_FROM='from@example.com'):
            mailhandler = MailHandler('IDENTIFIER')

        self.assertEqual(mailhandler.from_address, 'from@example.com')

    # send()
    def test_send(self):
        MailFactory()
        mailhandler = MailHandler('IDENTIFIER')
        mailhandler.to = "to@example.com"
        mailhandler.cc = "cc@example.com"
        mailhandler.bcc = "bcc@example.com"
        mailhandler.from_address = "from@example.com"
        mailhandler.body_strings = {'body_string_1': 'first body string',
                                    'body_string_2': 'second body string', }
        mailhandler.subject_strings = {'subject_string_1': 'first string',
                                       'subject_string_2': 'second string', }
        mailhandler.template = 'tests/mail.html'
        mailhandler.send()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, 'Subject first string and second string')
        self.assertEqual(mail.outbox[0].from_email, 'from@example.com')
        self.assertEqual(mail.outbox[0].to, ['to@example.com'])

    # _send()
    def test__send(self):
        msg = mail.EmailMultiAlternatives(
            "subject", "body", "from@example.com", ["to@example.com", ])
        MailHandler._send(msg)
        assert len(mail.outbox) == 1, "Inbox is not empty"

    # _validate_values()
    def test__validate_values(self):
        MailFactory()
        with self.settings(MAILING_MANAGER_DEFAULT_FROM=None):
            mailhandler = MailHandler('IDENTIFIER')

        with self.assertRaisesMessage(
            TypeError, "TemplateMail.to should be a string or an iterable."
        ):
            mailhandler._validate_values()

        # Setting .to, so we can test the .from_address validation
        mailhandler.to = "to@example.com"

        with self.assertRaisesMessage(
            TypeError, "TemplateMail.from_address needs to be a string."
        ):
            mailhandler._validate_values()

        mailhandler.from_address = ""
        with self.assertRaisesMessage(
            ValidationError,
            'Introdueix una adreça de correu electrònic vàlida'
        ):
            mailhandler._validate_values()

    # _setup_email()
    def test__setup_email(self):
        MailFactory()
        mailhandler = MailHandler('IDENTIFIER')
        mailhandler.to = "to@example.com"
        mailhandler.cc = "cc@example.com"
        mailhandler.bcc = "bcc@example.com"
        mailhandler.body_strings = {'body_string_1': 'first body string',
                                    'body_string_2': 'second body string', }
        mailhandler.subject_strings = {'subject_string_1': 'first string',
                                       'subject_string_2': 'second string', }
        mailhandler.template = 'tests/mail.html'
        msg = mailhandler._setup_email()

        self.assertIsInstance(msg, mail.EmailMultiAlternatives)

        self.assertListEqual(msg.cc, ['cc@example.com', ])
        self.assertListEqual(msg.bcc, ['bcc@example.com', ])

        # EmailMultiAlternatives appends HTML content in msg.alternatives list
        html_content = [
            (mailhandler.get_rendered_html_body(), "text/html"),
        ]
        self.assertListEqual(msg.alternatives, html_content)

    # _get_bcc_with_debugging_copy()
    def test__get_bcc_with_debugging_copy(self):
        MailFactory()
        mailhandler = MailHandler('IDENTIFIER')
        mailhandler.bcc = ("bcc@example.com", )

        compare_to = ["bcc@example.com", ]
        self.assertListEqual(
            mailhandler._get_bcc_with_debugging_copy(), compare_to)

        # Making sure that is not adding the debug BCC is DEBUG is False:
        mailhandler.debug_bcc = "debug1@example.com"
        with self.settings(DEBUG=False):
            self.assertListEqual(
                mailhandler._get_bcc_with_debugging_copy(), compare_to)

        compare_to = ["bcc@example.com", "debug1@example.com", ]
        with self.settings(DEBUG=True):
            self.assertListEqual(
                mailhandler._get_bcc_with_debugging_copy(), compare_to)

        mailhandler.debug_bcc = ("debug1@example.com", "debug2@example.com", )
        compare_to = [
            "bcc@example.com", "debug1@example.com", "debug2@example.com",
        ]
        with self.settings(DEBUG=True):
            self.assertListEqual(
                mailhandler._get_bcc_with_debugging_copy(), compare_to
            )

    # _normalize_to_iterable()
    def test__normalize_to_iterable(self):
        with self.assertRaisesMessage(
            TypeError, "Value '10 should be a string or an iterable."
        ):
            MailHandler._normalize_to_iterable(10)
