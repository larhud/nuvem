# Generated by Django 2.2.28 on 2022-07-25 12:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nuvem', '0020_documento_stopwords2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documento',
            name='stopwords2',
        ),
    ]