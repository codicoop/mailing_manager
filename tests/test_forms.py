from django.test import TestCase
from django import forms

from mailing_manager.forms import TemplateMailPreviewForm
from mailing_manager.mail_template import MailTemplate
from .factories.mail import MailFactory


class TemplateMailPreviewFormTest(TestCase):

    # __init__()
    def test_init(self):
        MailFactory()
        mailtemplate = MailTemplate('IDENTIFIER')

        # Prefixing with "subject_" or "body_" to fit the dynamic fields
        # formation naming:
        # data = {
        #     'subject_subject_string_1': 'aa',
        #     'subject_subject_string_2': 'aa',
        #     'body_body_string_1': 'aa',
        #     'body_body_string_2': 'aa'
        # }

        form = TemplateMailPreviewForm(mailtemplate)
        self.assertIsInstance(form, TemplateMailPreviewForm)

        # Checking base fields:
        self.assertIsInstance(form.fields['options_to'], forms.CharField)
        self.assertIsInstance(form.fields['options_now'], forms.BooleanField)

        # Checking that dynamic field creation worked fine:
        self.assertIsInstance(
            form.fields['subject_subject_string_1'], forms.CharField)
        self.assertIsInstance(
            form.fields['subject_subject_string_2'], forms.CharField)
        self.assertIsInstance(
            form.fields['body_body_string_1'], forms.CharField)
        self.assertIsInstance(
            form.fields['body_body_string_2'], forms.CharField)

        # Testing initial strings:
        self.assertEqual(
            form.fields['subject_subject_string_1'].initial, 'SUBJECT_STRING_1'
        )
        self.assertEqual(
            form.fields['subject_subject_string_2'].initial, 'SUBJECT_STRING_2'
        )
        self.assertEqual(
            form.fields['body_body_string_1'].initial, 'BODY_STRING_1')
        self.assertEqual(
            form.fields['body_body_string_2'].initial, 'BODY_STRING_2')
