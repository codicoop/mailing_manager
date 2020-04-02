import re
from django.db import models
from django.utils.translation import gettext as _
from django.template.defaultfilters import upper


class Mail(models.Model):
    created = models.DateTimeField(_("creation"), auto_now_add=True)
    text_identifier = models.CharField(_("identifier"), unique=True, max_length=100)
    subject = models.CharField(_("subject"), max_length=250)
    body = models.TextField(_("body"))
    default_template_path = models.CharField(_("default template path"), max_length=250, null=True, blank=True)

    @property
    def subject_strings(self):
        return re.findall(r"\{(.*?)\}", str(self.subject))

    @property
    def subject_strings_dict(self):
        dic = {}
        for item in self.subject_strings:
            dic.update({item: f"[{upper(item)}]"})
        return dic

    @property
    def body_strings(self):
        return re.findall(r"\{(.*?)\}", str(self.body))

    @property
    def body_strings_dict(self):
        dic = {}
        for item in self.body_strings:
            dic.update({item: f"[{upper(item)}]"})
        return dic

    def __str__(self):
        return self.text_identifier
