# Generated by Django 3.2 on 2021-04-16 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailing_manager', '0002_auto_20201211_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
