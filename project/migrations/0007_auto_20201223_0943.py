# Generated by Django 3.1.4 on 2020-12-23 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_auto_20201223_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indicators',
            name='example',
            field=models.CharField(max_length=100),
        ),
    ]