# Generated by Django 5.0.2 on 2024-05-05 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0003_alter_country_country_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='cover_img',
            field=models.ImageField(upload_to='destinations/cities/'),
        ),
        migrations.AlterField(
            model_name='country',
            name='flag',
            field=models.ImageField(null=True, upload_to='destinations/countries/'),
        ),
    ]
