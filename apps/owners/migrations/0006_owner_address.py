# Generated by Django 5.0.2 on 2024-05-15 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('owners', '0005_alter_owner_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='owner',
            name='address',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
