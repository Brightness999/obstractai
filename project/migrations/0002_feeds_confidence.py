# Generated by Django 3.1.4 on 2020-12-21 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feeds',
            name='confidence',
            field=models.PositiveIntegerField(null=True),
        ),
    ]