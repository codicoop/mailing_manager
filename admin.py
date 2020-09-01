from django.contrib import admin, messages
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .models import Mail
from .mail_queue_handler import MailQueueHandler
from .forms import TemplateMailPreviewForm


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ('text_identifier', 'subject', 'default_template_path', 'preview_field')
    readonly_fields = ('created', 'subject_strings', 'body_strings', )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                r'<_id>/preview/',
                self.admin_site.admin_view(self.preview_view),
                name='template-mail-preview'
            ),
            path(
                r'<_id>/preview_iframe/',
                self.admin_site.admin_view(self.preview_iframe_view),
                name='template-mail-preview-iframe'
            ),
        ]
        return custom_urls + urls

    def preview_field(self, obj):
        if obj.id is None:
            return '-'
        url = reverse('admin:template-mail-preview', kwargs={'_id': obj.id})
        txt = _('Preview and test')
        return mark_safe(
            f"<a href=\"{url}\">{txt}</a>")

    preview_field.short_description = _("Preview")

    def preview_view(self, request, _id):
        # Inspired by: https://gist.github.com/rsarai/d475c766871f40e52b8b4d1b12dedea2
        mail = Mail.objects.get(id=_id)
        template_mail = MailQueueHandler(mail.text_identifier)
        # Only setting up the subject because the body is handled by the iframe view:
        template_mail.subject_strings = template_mail.mail.subject_strings_dict

        if request.method == 'POST':
            form = TemplateMailPreviewForm(template_mail, request.POST)
            if form.is_valid():
                self._send_preview(form, template_mail)
                self.message_user(request, _("Test email successfully sent."))
                return HttpResponseRedirect("../../")
            else:
                messages.error(request, _("Error: all fields are required."))

        context = {
            **self.admin_site.each_context(request),
            'obj': mail,
            'opts': self.model._meta,
            'template_mail': template_mail,
            'rendered_subject': template_mail.get_rendered_subject(),
        }
        return TemplateResponse(
            request, 'admin/templatemail_preview.html', context)

    @xframe_options_sameorigin
    def preview_iframe_view(self, request, _id):
        mail = Mail.objects.get(id=_id)
        template_mail = MailQueueHandler(mail.text_identifier)
        template_mail.body_strings = template_mail.mail.body_strings_dict
        template_mail.request = request
        return HttpResponse(template_mail.get_rendered_html_body())

    def _send_preview(self, form, template_mail):
        for string in template_mail.mail.subject_strings:
            template_mail.subject_strings.update({string: form.cleaned_data[f"subject_{string}"]})

        for string in template_mail.mail.body_strings:
            template_mail.body_strings.update({string: form.cleaned_data[f"body_{string}"]})

        # From address might come filled with settings.MAILING_MANAGER_DEFAULT_FROM.
        if not template_mail.from_address:
            template_mail.from_address = form.cleaned_data['options_to']

        template_mail.to = form.cleaned_data['options_to']
        template_mail.send(form.cleaned_data['options_now'])
