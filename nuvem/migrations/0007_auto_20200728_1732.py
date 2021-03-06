# Generated by Django 2.2.14 on 2020-07-28 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nuvem', '0006_auto_20191102_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='tipo',
            field=models.CharField(blank=True, choices=[('simple_text', 'Texto Simples'), ('keywords', 'Palavras Chaves')], max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='documento',
            name='titulo',
            field=models.TextField(blank=True, null=True, verbose_name='Título do artigo/livro'),
        ),
    ]
