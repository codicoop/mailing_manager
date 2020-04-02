from django.test import TestCase

from .factories.mail import MailFactory


class MailQueueHandlerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.Mail = MailFactory._meta.model

    # model.Mail
    def test_mail_creation(self):
        mail = MailFactory()
        self.assertTrue(isinstance(mail, self.Mail))
        subject_strings = ('subject_string_1', 'subject_string_2', )
        self.assertSequenceEqual(subject_strings, mail.subject_strings)
        body_strings = ('body_string_1', 'body_string_2', )
        self.assertSequenceEqual(body_strings, mail.body_strings)

        subject_strings_dict = {'subject_string_1': '[SUBJECT_STRING_1]',
                               'subject_string_2': '[SUBJECT_STRING_2]', }
        self.assertEqual(subject_strings_dict, mail.subject_strings_dict)

        body_strings_dict = {'body_string_1': '[BODY_STRING_1]',
                             'body_string_2': '[BODY_STRING_2]', }
        self.assertEqual(body_strings_dict, mail.body_strings_dict)

        self.assertEqual(mail.__str__(), 'IDENTIFIER')
