# Generated by Django 2.2.28 on 2022-08-14 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nuvem', '0015_auto_20220813_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='consolidado',
            field=models.BooleanField(default=False),
        ),
    ]
