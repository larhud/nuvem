# Generated by Django 2.2.28 on 2022-07-25 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nuvem', '0019_auto_20220723_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='stopwords2',
            field=models.TextField(blank=True, null=True, verbose_name='Teste'),
        ),
    ]