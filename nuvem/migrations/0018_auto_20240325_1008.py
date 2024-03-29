# Generated by Django 2.2.28 on 2024-03-25 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nuvem', '0017_auto_20220815_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='colormap',
            field=models.CharField(default='viridis', max_length=20, verbose_name='Mapa de Cores'),
        ),
        migrations.AlterField(
            model_name='documento',
            name='font_type',
            field=models.CharField(blank=True, choices=[('Carlito-Regular.ttf', 'Carlito'), ('Comfortaa Bold.ttf', 'Comfortaa-Bold'), ('Cooper Regular.ttf', 'Cooper'), ('Lato-Regular.ttf', 'Lato-Regular'), ('Poppins-Regular.ttf', 'Poppins'), ('Lobster-Regular.ttf', 'Lobster')], max_length=40, null=True, verbose_name='Font Type'),
        ),
    ]
