# Mailing Manager library

## Why this library?

To provide a good answer to the following needs that we are facing:

- Organization of all the different e-mails that the system is going to send when they do certain actions.
- Apply HTML templates that will be shared among different e-mails.
- Log all the e-mails sent.
- Send the e-mails asynchronously to avoid having the user hanging until it's send, or facing a 500 if something goes 
wrong.
- Preview the resulting e-mail (mixing the body with the general template) when setting it up.
- Send test e-mails to test both the mailing engine and to preview them in email clients.

## Usage

To programmatically send emails, you need:

1. Create the Mail item in the database using the administration panel and give it a unique Identifier, as well as a 
subject and body, using bracket strings for the {variables}.
2. Whereas you want to send an e-mail in the code, instantiate proper mail handler class, passing the identifier,
as explained below.
3. Fill the object parameters and .send() it.

## Dependencies

### for mail_handler.py

The MailHandler class uses Django's native e-mail handling library, so you need to set up the email back-end to SMTP
and the SMTP configuration according to Django's documentation.

### for mail_queue_handler.py

The MailQueueHandler class extends MailHandler to use [https://github.com/Privex/django-mail-queue](django_mail_queue) 
to send the emails asynchronously and to keep a log of everything sent.
If you don't need these features just stick to MailHandler.

In addition to setting up Django's email configuration, you'll need:
- To follow the instructions of mail_queue's documentation to install it properly.
- Deploy a way to periodically launch the sending of the queued e-mails. Most typically is Cron or Celery, but if you are 
using Docker, we recommend you to take a look at [https://hub.docker.com/r/willfarrell/ofelia](Ofelia).

## Installation

1. Install dependencies.
2. Add the library to INSTALLED_APPS and run `python manage.py migrate`.

The Admin panel should show either the mail_queue email log and the mailing_manager Mail model sections,
unless you are using custom dashboards and you need to include them manually. 

## Example

Having created a Mail item in the database with this information:
subject = "{name} {surname} here's your daily weather report"
body = "Today was {today_weather}, tomorrow's forecast is: {tomorrow_weather}"
text_identifier = 'WEATHER_REPORT'

Wherever you want your app to send this e-mail, do this:

    mail = MailQueueHandler('WEATHER_REPORT')
    mail.from_address = 'from@example.com'
    mail.to = ('a@example.com', 'b@example.com',)
    mail.cc = ('c.example.com', 'd@example.com',)
    mail.bcc = ('e.example.com', 'f@example.com',)
    mail.subject_strings = {
        'name': 'Joan',
        'surname': 'Serrallonga',
    }
    mail.body_strings = {
        'today_weather': 'Cloudy',
        'tomorrow_weather': 'Sunny',
    }
    mail.send() # or mail.send(now=True)

## E-mail debugging

The library can automatically add one or more recipients to BCC for debugging purposes.
To enable that, you need the DEBUG enabled in settings:

    DEBUG = True

And to specify the recipient or recipients (takes strings and iterables):

    mail.debug_bcc = "debug@example.com"

## Log cleanup

By default, every time an e-mail is send it prunes all the sent e-mails that are older than 30
days that mail_queue is keeping.

You can change that by setting this value before calling send():

    mail.prune_older_than = 5  # to delete the ones older than 5 days
    mail.prune_older_than = None  # to disable this behavior.

## Templating

The library will use the Django templating engine to combine the body that you configured in the database with a 
template that you might place in your file tree.

Create a template in your templates folder following this example:
```
{% autoescape off %}
<h1>Mail header and other stuff</h1>

{{ mail_content }}

<h2>footer and so</h2>
{% endautoescape %}
``` 

So, making sure you are disabling autoescaping and including `mail_content` somewhere.

Then you just need to specify the template when setting up the sending:

    mail.template = 'path/to/your/template.html'
    
> **_NOTE ABOUT CONTEXT PREPROCESSORS:_**  Passing along `request` is needed in order to use context from the 
> preprocessors in the template. When setting up the mailing manager object, you can set `MailingManagerInstance.request.`
>   
## Previewing and sending test emails

Create a Mail record using the admin panel and you'll see the link to Preview at the last column.

That will show you the resulting rendered HTML, including the template if you specified a default_template_path for it.

Underneath there's a form that lets you enter values for each of the variable strings that you specified in both subject
and body (the {variable_string} ones).

You just need to fill this form in order to send a sample email to the address that you specified. Of course remember that
if you are not using the "Send now" option, it's going to be stored in the mail_queue's queue until you trigger the
queue's processing.

That Preview section is only for MailQueueHandler. Compatibility for the basic MailHandler class might be added 
eventually.

## Developing

This is my first public library, I tried to be as organized as possible but many things are going to need improvement, so,
handle with love!
I'll be very happy to hear any suggestion, idea or problems that you encounter.

Remember to run tests before and after touching anything.

## Translating

Basically use Django's translation functionalities.

To update the .po language files after making changes, move to the app folder and launch:

    django-admin makemessages -l ca
    
Where "ca" is the language locale you want to generate.

Then do the translations (using Poedit i.e.) and afterwards compile them with:

    django-admin compilemessages
    
Also from the app's folder.