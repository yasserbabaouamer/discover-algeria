from django.db.models import TextChoices


class TourStatus(TextChoices):
    VISIBLE = 'Visible'
    HIDDEN = 'Hidden'
    DELETED = 'Deleted'


class ScheduledTourStatus(TextChoices):
    ACTIVE = 'Active'
    CANCELLED = 'Cancelled'





