# Generated by Django 5.0.2 on 2024-05-13 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0006_guest_about'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='address',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
