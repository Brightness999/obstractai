# Generated by Django 3.1.4 on 2021-01-18 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0043_auto_20210118_2220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feeds',
            name='confidence',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='feeds',
            name='manage_enabled',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='feeds',
            name='tags',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
