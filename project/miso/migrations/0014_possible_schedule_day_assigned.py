# Generated by Django 2.0.5 on 2018-05-22 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miso', '0013_auto_20180521_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='possible_schedule',
            name='day_assigned',
            field=models.BooleanField(default=False),
        ),
    ]
