from django.contrib.admin import AdminSite
from django.test import TestCase

from .factories.mail import MailFactory
from ..admin import MailAdmin
from ..models import Mail


class TemplateMailPreviewFormTest(TestCase):

    def setUp(self):
        self.mail = MailFactory()
        self.site = AdminSite()
        self.post_data = {
            'options_to': 'to@example.com',
            'options_now': False,
            'subject_subject_string_1': 'aa',
            'subject_subject_string_2': 'aa',
            'body_body_string_1': 'aa',
            'body_body_string_2': 'aa'
        }

    # preview_field()
    def test_preview_field(self):
        admin = MailAdmin(Mail, self.site)
        compare_to = '<a href="/admin/mailing_manager/mail/8/preview/">Previsualització i prova</a>'
        self.assertEqual(admin.preview_field(self.mail), compare_to)

        # Now instantiating the model without loading any record to test obj.id = None:
        compare_to = '-'
        self.assertEqual(admin.preview_field(Mail()), compare_to)
