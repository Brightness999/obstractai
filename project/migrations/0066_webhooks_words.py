# Generated by Django 3.1.4 on 2021-02-04 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0065_auto_20210204_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhooks',
            name='words',
            field=models.CharField(default='', max_length=100),
        ),
    ]
