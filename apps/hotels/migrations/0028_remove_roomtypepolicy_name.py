# Generated by Django 5.0.2 on 2024-05-04 21:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0027_remove_roomtypepolicy_breakfast_included_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roomtypepolicy',
            name='name',
        ),
    ]
