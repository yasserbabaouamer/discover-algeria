# Generated by Django 5.0.2 on 2024-04-05 10:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0002_city_description_country_country_code_and_more'),
        ('touristicagencies', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='touristicagency',
            name='country',
        ),
        migrations.AddField(
            model_name='touristicagency',
            name='address',
            field=models.CharField(max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='touristicagency',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='touristic_agencies', to='destinations.city'),
        ),
        migrations.AlterField(
            model_name='periodictourregistration',
            name='scheduled_tour',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registrations', to='touristicagencies.scheduledtour'),
        ),
    ]
