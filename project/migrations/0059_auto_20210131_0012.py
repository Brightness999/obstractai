# Generated by Django 3.1.4 on 2021-01-31 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0058_delete_extractions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='globalindicators',
            name='enabled',
        ),
        migrations.RemoveField(
            model_name='globalindicators',
            name='user',
        ),
    ]
