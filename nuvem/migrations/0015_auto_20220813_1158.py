# Generated by Django 2.2.28 on 2022-08-13 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nuvem', '0014_auto_20220613_1814'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='font_type',
            field=models.CharField(blank=True, choices=[('Carlito-Regular.ttf', 'Carlito'), ('Comfortaa Bold.ttf', 'Comfortaa-Bold'), ('Cooper Regular.ttf', 'Cooper'), ('Lato-Regular.ttf', 'Lato-Regular'), ('Poppins-Regular.ttf', 'Poppins')], max_length=40, null=True, verbose_name='Font Type'),
        ),
        migrations.AddField(
            model_name='documento',
            name='status',
            field=models.CharField(choices=[('A', 'Aberto'), ('P', 'Programado'), ('F', 'Finalizado'), ('E', 'Com erro')], default='A', max_length=1),
        ),
    ]
