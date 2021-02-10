# Generated by Django 3.1.4 on 2021-02-03 07:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0062_feeds_intelgroup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='intelreports',
            name='feed',
        ),
        migrations.AddField(
            model_name='intelreports',
            name='groupfeed',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='project.groupfeeds'),
        ),
    ]