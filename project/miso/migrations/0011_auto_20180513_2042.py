# Generated by Django 2.0.5 on 2018-05-13 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('miso', '0010_day_needs_newcomer'),
    ]

    operations = [
        migrations.AddField(
            model_name='day',
            name='real_newcomer',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='day',
            name='real_origin',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
