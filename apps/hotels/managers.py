from datetime import datetime

from django.db import models
from django.db.models import Q, QuerySet, OuterRef, Count

from apps.hotels.enums import ReservationStatus
from apps.owners.models import Owner
from .models import *


class RoomManager(models.Manager):
    def find_available_rooms_by_room_type(self, room_type_id: int, check_in: datetime, check_out: datetime) -> QuerySet:
        reserved_rooms = self.filter(
            Q(status=RoomStatus.VISIBLE) &
            Q(room_type_id=room_type_id) &
            Q(assignments__reserved_room_type__reservation__status=ReservationStatus.CONFIRMED.value) |
            Q(assignments__reserved_room_type__reservation__status=ReservationStatus.ACTIVE.value)
            & (
                    Q(assignments__reserved_room_type__reservation__check_in__gt=check_in) &
                    Q(assignments__reserved_room_type__reservation__check_in__lt=check_out)
                    |
                    Q(assignments__reserved_room_type__reservation__check_in__lte=check_in) &
                    Q(assignments__reserved_room_type__reservation__check_out__gte=check_out)
                    |
                    Q(assignments__reserved_room_type__reservation__check_out__gt=check_in) &
                    Q(assignments__reserved_room_type__reservation__check_out__lt=check_out)
            )
        ).all()
        reserved_rooms_ids = reserved_rooms.values_list('id', flat=True)
        available_rooms = self.filter(room_type_id=room_type_id,status=RoomStatus.VISIBLE).exclude(id__in=reserved_rooms_ids).all()
        return available_rooms

    def get_room_type_rooms_subquery(self):
        return self.filter(
            room_type_id=OuterRef('pk')
        ).annotate(
            rooms_count=Count('id')
        )

