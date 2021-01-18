# Generated by Django 3.1.4 on 2020-12-30 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0016_feeds_intelgroup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedchannels',
            name='example',
        ),
        migrations.RemoveField(
            model_name='feedchannels',
            name='required',
        ),
        migrations.RemoveField(
            model_name='feeditems',
            name='example',
        ),
        migrations.RemoveField(
            model_name='feeditems',
            name='required',
        ),
        migrations.AlterField(
            model_name='feedchannels',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='feedchannels',
            name='element',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='feeditems',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='feeditems',
            name='element',
            field=models.TextField(),
        ),
    ]
