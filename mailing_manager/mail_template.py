from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from django.template.loader import render_to_string
import re

from .models import Mail


class MailTemplate:
    subject_strings = {}
    body_strings = {}
    mail = None
    template = None
    template_extra_context = None
    request = None

    def __init__(self, text_identifier):
        self.mail = Mail.objects.get(text_identifier=text_identifier)

    def get_rendered_subject(self):
        self._validate_subject_strings()
        return self._get_formatted_text(
            strings=self.subject_strings, text=self.mail.subject
        )[:250]

    def get_rendered_html_body(self):
        self._validate_body_strings()
        txt = self._get_formatted_text(
            strings=self.body_strings, text=self.mail.body)
        if self._get_template_path() is not None:
            return self._apply_template(txt, self.template_extra_context)
        return mark_safe(txt)

    def get_plain_text_body(self):
        """
        Many email templates will incude the <style> block at header, even if
        the styles had been inlined, causing the
        plain text version to contain all the styles if you only strip_tags().

        :return: String without the HTML tags and any <styles> block removed.
        """
        text = re.sub(
            '<style>.*</style>', '', self.get_rendered_html_body(), flags=re.S
        )
        text = strip_tags(text)
        return text

    def _get_template_path(self):
        if self.template:
            return self.template
        if self.mail.default_template_path:
            return self.mail.default_template_path
        return None

    def _apply_template(self, content, template_extra_context=None):
        """
        Takes the specified self._get_template_path() (if any) and renders it,
        passing along the self.template_extra_content
        to the template.
        Using render_to_string here to access to full features of Django
        templating.
        :return: str with the rendered HTML.
        """
        if not self._get_template_path():
            return

        context_data = {
            'mail_content': content,
            **(template_extra_context or {}),
        }
        return render_to_string(
            self._get_template_path(), context_data, request=self.request
        )

    def _validate_subject_strings(self):
        missing_strings = []
        for string in self.mail.subject_strings:
            if string not in self.subject_strings:
                missing_strings.append(string)
        if len(missing_strings) > 0:
            raise ValueError(
                f"TemplateMail is trying to send the e-mail "
                f"{self.mail.text_identifier}, but these strings are missing "
                f"from subject_strings: {', '.join(missing_strings)}."
            )

    def _validate_body_strings(self):
        missing_strings = []
        for string in self.mail.body_strings:
            if string not in self.body_strings:
                missing_strings.append(string)
        if len(missing_strings) > 0:
            raise ValueError(
                f"TemplateMail is trying to send the e-mail "
                f"{self.mail.text_identifier}, but these stringsare missing "
                f"from body_strings: {', '.join(missing_strings)}."
            )

    @staticmethod
    def _get_formatted_text(strings, text):
        return text.format(**strings)
