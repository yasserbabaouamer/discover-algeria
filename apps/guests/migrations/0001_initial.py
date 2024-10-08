# Generated by Django 5.0.2 on 2024-04-03 13:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('destinations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255, null=True)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('birthday', models.DateField(null=True)),
                ('phone', models.CharField(max_length=20, null=True)),
                ('profile_pic', models.ImageField(null=True, upload_to='')),
                ('preferred_currency', models.CharField(choices=[('DZD', 'Dzd'), ('EUR', 'Eur'), ('USD', 'Usd')], default='DZD', max_length=3)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('country', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='guests', to='destinations.country')),
            ],
            options={
                'db_table': 'guests',
            },
        ),
    ]
