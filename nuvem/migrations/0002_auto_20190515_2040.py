# Generated by Django 2.2.1 on 2019-05-15 23:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nuvem', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='age',
            new_name='idade',
        ),
    ]
