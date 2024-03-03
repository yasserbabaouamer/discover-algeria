from django.db.models import TextChoices


class Currency(TextChoices):
    DZD = 'DZD'
    EUR = 'EUR'
    USD = 'USD'


class AccountStatus(TextChoices):
    ACTIVE = 'Active'
    BANNED = 'Banned'
    DELETED_BY_USER = 'Deleted By User'
    DELETED_BY_ADMIN = 'Deleted By Admin'


class IdentityStatus(TextChoices):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REFUSED = 'Refused'
