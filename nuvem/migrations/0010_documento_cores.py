# Generated by Django 2.2.14 on 2020-07-30 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nuvem', '0009_documento_chave'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='cores',
            field=models.BooleanField(default=False),
        ),
    ]
