# Generated by Django 5.0.2 on 2024-05-08 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0006_alter_cityimage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='iso',
            field=models.CharField(max_length=2, null=True),
        ),
    ]
