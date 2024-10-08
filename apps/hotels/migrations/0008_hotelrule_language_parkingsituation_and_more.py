# Generated by Django 5.0.2 on 2024-04-27 17:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0007_reservation_hotel_alter_reservedroomtype_room_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='HotelRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in', models.TimeField()),
                ('check_out', models.TimeField()),
                ('cancellation_policy', models.CharField(choices=[('No Cancellation Policy', 'No'), ('Cancellation Depends on Selected Room Type', 'Depends'), ('Fixed Cancellation Before', 'Fixed')], max_length=255)),
                ('days_before_cancellation', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'hotel_rules',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'languages',
            },
        ),
        migrations.CreateModel(
            name='ParkingSituation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reservation_needed', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('Private', 'Private'), ('Public', 'Public')], max_length=25)),
            ],
            options={
                'db_table': 'parking_situations',
            },
        ),
        migrations.RemoveField(
            model_name='roomtype',
            name='main_bed_type',
        ),
        migrations.AddField(
            model_name='roomtype',
            name='bed_types',
            field=models.ManyToManyField(db_table='room_type_beds', to='hotels.bedtype'),
        ),
        migrations.AddConstraint(
            model_name='hotelrule',
            constraint=models.CheckConstraint(check=models.Q(('cancellation_policy__in', ['No Cancellation Policy', 'Cancellation Depends on Selected Room Type', 'Fixed Cancellation Before'])), name='chk_cancellation_policy'),
        ),
        migrations.AddField(
            model_name='hotel',
            name='staff_languages',
            field=models.ManyToManyField(db_table='hotel_staff_languages', to='hotels.language'),
        ),
        migrations.AddField(
            model_name='parkingsituation',
            name='hotel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parking_situation', to='hotels.hotel'),
        ),
        migrations.AddConstraint(
            model_name='parkingsituation',
            constraint=models.CheckConstraint(check=models.Q(('type__in', ['Private', 'Public'])), name='chk_parking_type'),
        ),
    ]
