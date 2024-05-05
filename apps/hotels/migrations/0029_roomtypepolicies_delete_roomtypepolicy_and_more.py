# Generated by Django 5.0.2 on 2024-05-04 21:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0028_remove_roomtypepolicy_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomTypePolicies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cancellation_policy', models.CharField(choices=[('No Cancellation', 'No'), ('Cancellation Before', 'Before')], max_length=255, null=True)),
                ('days_before_cancellation', models.PositiveIntegerField(default=0)),
                ('prepayment_policy', models.CharField(choices=[('Prepayment is not required', 'Not Required'), ('Prepayment is required', 'Required')], max_length=255, null=True)),
                ('room_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='policies', to='hotels.roomtype')),
            ],
            options={
                'db_table': '_room_type_policy',
            },
        ),
        migrations.DeleteModel(
            name='RoomTypePolicy',
        ),
        migrations.AddConstraint(
            model_name='roomtypepolicies',
            constraint=models.CheckConstraint(check=models.Q(('cancellation_policy__in', ['No Cancellation', 'Cancellation Before'])), name='chk_room_type_cancellation_policy'),
        ),
        migrations.AddConstraint(
            model_name='roomtypepolicies',
            constraint=models.CheckConstraint(check=models.Q(('prepayment_policy__in', ['Prepayment is not required', 'Prepayment is required'])), name='chk_room_type_prepayment_policy'),
        ),
    ]
