# Generated by Django 5.0.2 on 2024-04-19 05:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0002_city_description_country_country_code_and_more'),
        ('touristicagencies', '0002_remove_touristicagency_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='periodictourregistration',
            name='country_code',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='destinations.country'),
        ),
        migrations.AlterField(
            model_name='periodictourregistration',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tour_registrations', to='destinations.country'),
        ),
    ]
