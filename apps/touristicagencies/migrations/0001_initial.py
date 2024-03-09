# Generated by Django 5.0.2 on 2024-03-09 11:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Guide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('email', models.EmailField(max_length=255)),
                ('contact', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'guides',
            },
        ),
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=500)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('price', models.IntegerField()),
            ],
            options={
                'db_table': 'tours',
            },
        ),
        migrations.CreateModel(
            name='TouristicAgency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=300)),
                ('website_url', models.URLField(null=True)),
                ('cover_img', models.URLField(null=True)),
            ],
            options={
                'db_table': 'touristic_agencies',
            },
        ),
        migrations.CreateModel(
            name='TourImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='')),
                ('tour', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='images', to='touristicagencies.tour')),
            ],
            options={
                'db_table': 'tour_images',
            },
        ),
    ]
