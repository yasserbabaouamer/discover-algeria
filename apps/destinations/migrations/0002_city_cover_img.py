# Generated by Django 5.0.2 on 2024-03-17 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='cover_img',
            field=models.ImageField(default='img', upload_to=''),
        ),
    ]
