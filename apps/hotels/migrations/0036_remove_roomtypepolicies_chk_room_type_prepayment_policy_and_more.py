# Generated by Django 5.0.2 on 2024-05-08 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0035_alter_bedtype_icon'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='roomtypepolicies',
            name='chk_room_type_prepayment_policy',
        ),
        migrations.AlterField(
            model_name='roomtypepolicies',
            name='prepayment_policy',
            field=models.CharField(choices=[('Prepayment is not required', 'Not Required'), ('Prepayment is required', 'Required')], max_length=255, null=True),
        ),
        migrations.AddConstraint(
            model_name='roomtypepolicies',
            constraint=models.CheckConstraint(check=models.Q(('prepayment_policy__in', ['Prepayment is not required', 'Prepayment is required'])), name='chk_room_type_prepayment_policy'),
        ),
    ]
