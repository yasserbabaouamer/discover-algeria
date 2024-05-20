# reservations/migrations/0002_add_periodic_task.py
from django.db import migrations
from django_celery_beat.models import PeriodicTask, IntervalSchedule


def create_update_reservations_task(apps, schema_editor):
    # Get or create the interval schedule
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.HOURS,
    )

    # Create the periodic task
    PeriodicTask.objects.create(
        interval=schedule,
        name='Update reservations every hour',
        task='reservations.tasks.update_reservations',
    )


class Migration(migrations.Migration):
    dependencies = [
        ('reservations', '0001_initial'),
        ('django_celery_beat', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_update_reservations_task),
    ]
