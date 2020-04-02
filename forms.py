from django import forms
from django.template.defaultfilters import upper


class TemplateMailPreviewForm(forms.Form):
    options_to = forms.CharField(initial="someone@example.com", required=True)
    options_now = forms.BooleanField(required=False)

    def __init__(self, template_mail, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for string in template_mail.mail.subject_strings:
            field_name = f"subject_{string}"
            # Setting up 'initial' even though in the template we are not rendering it from the Form object yet.
            self.fields[field_name] = forms.CharField(required=True, initial=upper(string))
            self.initial[field_name] = string

        for string in template_mail.mail.body_strings:
            field_name = f"body_{string}"
            self.fields[field_name] = forms.CharField(required=True, initial=upper(string))
            self.initial[field_name] = string
