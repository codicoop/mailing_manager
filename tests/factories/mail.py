import factory

from mailing_manager.models import Mail


class MailFactory(factory.DjangoModelFactory):
    class Meta:
        model = Mail
        django_get_or_create = ('text_identifier', 'subject', 'body', )

    text_identifier = 'IDENTIFIER'
    subject = "Subject {subject_string_1} and {subject_string_2}"
    body = "Body: {body_string_1} and {body_string_2}"
    default_template_path = ''
