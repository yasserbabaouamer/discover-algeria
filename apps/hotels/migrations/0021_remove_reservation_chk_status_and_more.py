# Generated by Django 5.0.2 on 2024-05-01 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0003_alter_country_country_code'),
        ('guests', '0005_alter_guest_profile_pic'),
        ('hotels', '0020_reservation_commission'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='reservation',
            name='chk_status',
        ),
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.CharField(choices=[('Confirmed', 'Confirmed'), ('Active', 'Active'), ('Cancelled By Owner', 'Cancelled By Owner'), ('Cancelled By Guest', 'Cancelled By Guest'), ('Completed', 'Completed'), ('Deleted_By_Admin', 'Deleted By Admin')], default='Confirmed', max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='reservedroomtype',
            unique_together={('reservation', 'room_type')},
        ),
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.CheckConstraint(check=models.Q(('status__in', ['Confirmed', 'Active', 'Cancelled By Owner', 'Cancelled By Guest', 'Completed', 'Deleted_By_Admin'])), name='chk_status'),
        ),
    ]
