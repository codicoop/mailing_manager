# Generated by Django 2.2.7 on 2021-04-22 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing_manager', '0003_alter_mail_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
