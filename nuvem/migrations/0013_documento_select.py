# Generated by Django 2.2.24 on 2021-07-18 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nuvem', '0012_auto_20210625_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='select',
            field=models.CharField(blank=True, choices=[('portuguese', 'PT'), ('spanish', 'ES'), ('english', 'EN')],
                                   max_length=12, null=True),
        ),
    ]
