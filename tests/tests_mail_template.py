from django.test import TestCase

from apps.mailing_manager.models import Mail
from apps.mailing_manager.mail_template import MailTemplate
from .factories.mail import MailFactory


class MailQueueHandlerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.Mail = MailFactory._meta.model

    def create_mail(self,
                    text_identifier="IDENTIFIER",
                    subject="Subject {subject_string_1} and {subject_string_2}",
                    body="Body: {body_string_1} and {body_string_2}"):
        self.mail, created = Mail.objects.get_or_create(
            text_identifier=text_identifier,
            subject=subject,
            body=body
        )

    # get_rendered_subject()
    def test_get_rendered_subject(self):
        MailFactory()
        mailtemplate = MailTemplate('IDENTIFIER')
        mailtemplate.subject_strings = {'subject_string_1': 'first string',
                                        'subject_string_2': 'second string', }
        expected_text = "Subject first string and second string"
        self.assertEqual(mailtemplate.get_rendered_subject(), expected_text)

    # get_rendered_html_body()
    def test_get_rendered_html_body(self):
        MailFactory()
        mailtemplate = MailTemplate('IDENTIFIER')
        mailtemplate.body_strings = {'body_string_1': 'first body string',
                                     'body_string_2': 'second body string', }
        expected_text = "Body: first body string and second body string"
        self.assertEqual(mailtemplate.get_rendered_html_body(), expected_text)

        mailtemplate.template = 'tests/mail.html'
        expected_html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
  <head>
    <style>
        /* something */
    </style>
  <body>
  <p>
      Body: first body string and second body string
  </p>
  <p>
    Static content in the template.
  </p>
  </body>
</html>"""
        self.assertEqual(mailtemplate.get_rendered_html_body(), expected_html)
        # TODO: Specify a template and test that it returns it inside the template.

    # get_plain_text_body()
    def test_get_plain_text_body(self):
        MailFactory()
        mailtemplate = MailTemplate('IDENTIFIER')
        mailtemplate.body_strings = {'body_string_1': 'first body string',
                                     'body_string_2': 'second body string', }
        mailtemplate.template = 'tests/mail.html'
        expected_text = """

  
    
  
  
      Body: first body string and second body string
  
  
    Static content in the template.
  
  
"""
        self.assertEqual(mailtemplate.get_plain_text_body(), expected_text)

    # _get_template_path()
    def test__get_template_path(self):
        MailFactory(default_template_path='test/path.html')
        mailtemplate = MailTemplate('IDENTIFIER')
        self.assertEqual(mailtemplate._get_template_path(), 'test/path.html')

    # _apply_template()
    def test__apply_template(self):
        MailFactory()
        mailtemplate = MailTemplate('IDENTIFIER')
        self.assertEqual(mailtemplate._apply_template("dummy content"), None)

    # _validate_subject_strings()
    def test__validate_subject_strings(self):
        MailFactory()
        mailtemplate = MailTemplate('IDENTIFIER')
        expected_error = "TemplateMail is trying to send the e-mail IDENTIFIER, but these strings are missing from " \
                         "subject_strings: subject_string_1, subject_string_2."
        with self.assertRaisesMessage(ValueError, expected_error):
            mailtemplate._validate_subject_strings()

    # _validate_body_strings()
    def test__validate_body_strings(self):
        MailFactory()
        mailtemplate = MailTemplate('IDENTIFIER')
        expected_error = "TemplateMail is trying to send the e-mail IDENTIFIER, but these strings are missing from " \
                         "body_strings: body_string_1, body_string_2."
        with self.assertRaisesMessage(ValueError, expected_error):
            mailtemplate._validate_body_strings()

    # _get_formatted_text()
    def test_get_formatted_text(self):
        input_text = "Text with f strings: {first} and {second}"
        input_strings = {
            'first': 'LOREM',
            'second': 'IPSUM',
        }
        expected_text = "Text with f strings: LOREM and IPSUM"
        self.assertEqual(MailTemplate._get_formatted_text(input_strings, input_text), expected_text)
