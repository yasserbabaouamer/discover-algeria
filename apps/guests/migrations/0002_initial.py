# Generated by Django 5.0.2 on 2024-04-03 13:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('guests', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='guest', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='guest',
            constraint=models.CheckConstraint(check=models.Q(('preferred_currency__in', ['DZD', 'EUR', 'USD'])), name='chk_pref_currency'),
        ),
    ]
