# Generated by Django 3.1.4 on 2021-03-05 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0072_auto_20210222_1240'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='intelreports',
            options={'verbose_name_plural': 'IntelReports'},
        ),
        migrations.RemoveField(
            model_name='intelreports',
            name='groupfeed',
        ),
        migrations.RemoveField(
            model_name='intelreports',
            name='intelgroup',
        ),
    ]
