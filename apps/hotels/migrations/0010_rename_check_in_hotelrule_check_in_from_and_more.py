# Generated by Django 5.0.2 on 2024-04-28 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0009_hotel_country_code_hotel_created_at_hotel_updated_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hotelrule',
            old_name='check_in',
            new_name='check_in_from',
        ),
        migrations.RenameField(
            model_name='hotelrule',
            old_name='check_out',
            new_name='check_in_until',
        ),
        migrations.AddField(
            model_name='hotelrule',
            name='check_out_from',
            field=models.TimeField(default='18:00:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hotelrule',
            name='check_out_until',
            field=models.TimeField(default='18:00:00'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='hotelrule',
            name='days_before_cancellation',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
