from __future__ import absolute_import, unicode_literals

from celery import current_app

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

# from apps.reservations import tasks  # This will ensure tasks are imported and registered
print("We are initializing things")
print(current_app.tasks.keys())
__all__ = ('celery_app',)
