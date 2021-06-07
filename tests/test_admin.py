from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

from .factories.mail import MailFactory
from mailing_manager.admin import MailAdmin
from mailing_manager.models import Mail
from mailing_manager.mail_template import MailTemplate

User = get_user_model()


class MockSuperUser:
    is_active = True
    is_staff = True

    def has_perm(self, perm):
        return True


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
        user = User.objects.create_superuser(
            username='test',
            password='test',
        )
        self.client.force_login(user)

    # preview_field()
    def test_preview_field(self):
        admin = MailAdmin(Mail, self.site)
        compare_to = (
            '<a href="/admin/mailing_manager/mail/8/preview/">'
            'Previsualització i prova</a>'
        )
        self.assertEqual(admin.preview_field(self.mail), compare_to)

        # Now instantiating the model without loading any record to
        # test obj.id = None:
        compare_to = '-'
        self.assertEqual(admin.preview_field(Mail()), compare_to)

    # get_rendered_html_body()
    # url: /admin/mailing_manager/mail/{mailtemplate.mail.id}/preview_iframe/
    def test_preview_iframe_view(self):
        MailFactory()
        mailtemplate = MailTemplate('IDENTIFIER')
        mailtemplate.mail.default_template_path = 'tests/mail.html'
        mailtemplate.mail.save()
        expected_html = b"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
  <head>
    <style>
        /* something */
    </style>
  <body>
  <p>
      Body: [BODY_STRING_1] and [BODY_STRING_2]
  </p>
  <p>
    Static content in the template.
  </p>
  </body>
</html>"""  # noqa
        request_factory = RequestFactory()
        request = request_factory.get("/admin/")
        request.user = MockSuperUser()
        admin = MailAdmin(Mail, self.site)
        response = admin.preview_iframe_view(request, mailtemplate.mail.id)
        self.assertEqual(response.content, expected_html)

    # preview_view()
    def test_preview_view(self):
        MailFactory()
        mailtemplate = MailTemplate('IDENTIFIER')
        mailtemplate.mail.default_template_path = 'tests/mail.html'
        mailtemplate.mail.save()
        request_factory = RequestFactory()
        request = request_factory.get("/admin/")
        request.user = MockSuperUser()
        # admin = MailAdmin(Mail, self.site)
        # response = admin.preview_view(request, mailtemplate.mail.id)
        response = self.client.get(
            f"/admin/mailing_manager/mail/{mailtemplate.mail.id}"
            f"/preview_iframe/"
        )
        print(response.content)
        self.assertContains(response.content, "test")
