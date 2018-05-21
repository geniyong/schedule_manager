# Generated by Django 2.0.5 on 2018-05-21 00:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('miso', '0011_auto_20180513_2042'),
    ]

    operations = [
        migrations.CreateModel(
            name='Still_possible_schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='miso.Day')),
            ],
        ),
        migrations.AddField(
            model_name='staff',
            name='max_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='staff',
            name='min_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='still_possible_schedule',
            name='staff_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='miso.Staff'),
        ),
        migrations.AlterUniqueTogether(
            name='still_possible_schedule',
            unique_together={('staff_id', 'day_id')},
        ),
    ]