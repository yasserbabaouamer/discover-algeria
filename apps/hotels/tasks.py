from datetime import datetime, timezone

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.hotels.enums import ReservationStatus
from apps.hotels.models import Reservation
from core.celery import app


@app.task
def update_reservations():
    print("update reservations is running ...")
    now = timezone.now()
    reservations = Reservation.objects.all()
    for reservation in reservations:
        if reservation.status == ReservationStatus.CONFIRMED and reservation.check_in <= now:
            reservation.status = ReservationStatus.ACTIVE
            reservation.save()
        elif reservation.status == ReservationStatus.ACTIVE and reservation.check_out <= now:
            reservation.status = ReservationStatus.COMPLETED
            reservation.save()
    return "Done"
