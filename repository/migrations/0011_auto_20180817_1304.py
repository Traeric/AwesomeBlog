# Generated by Django 2.0.7 on 2018-08-17 05:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0010_trouble'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trouble',
            options={'verbose_name_plural': '报障表'},
        ),
        migrations.AlterModelTable(
            name='trouble',
            table='Trouble',
        ),
    ]