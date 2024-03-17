# Generated by Django 5.0.2 on 2024-03-17 11:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('touristicagencies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='touristicagency',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agency', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tour',
            name='touristic_agency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET, related_name='tours', to='touristicagencies.touristicagency'),
        ),
        migrations.AddField(
            model_name='guide',
            name='touristic_agency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guides', to='touristicagencies.touristicagency'),
        ),
    ]
