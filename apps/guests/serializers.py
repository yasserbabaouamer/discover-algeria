from django.core.validators import RegexValidator
from django.utils.html import escape
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_dataclasses.serializers import DataclassSerializer

from apps.destinations.serializers import CountrySerializer
from apps.guests.dtos import GuestTokens
from apps.guests.models import Guest


class GuestLoginRequestSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)


class QuickProfileRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    profile_pic = serializers.ImageField(required=False)

    def validate_first_name(self, value):
        return escape(value)

    def validate_last_name(self, value):
        return escape(value)


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    overall_rating = serializers.FloatField()
    country = CountrySerializer()
    role = serializers.SerializerMethodField()
    reservations = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    def get_phone(self, profile: Guest):
        return {
            'id': profile.country_code.id if profile.country_code is not None else None,
            'number': profile.phone,
            'code': profile.country_code.country_code if profile.country_code is not None else None,
            'flag': profile.country_code.flag.url if profile.country_code is not None else None
        }

    def get_email(self, guest: Guest):
        return guest.user.email

    def get_role(self, guest: Guest):
        return "guest"

    def get_reservations(self, guest: Guest):
        return [
            {
                "id": reservation.id,
                "total_price": reservation.total_price,
                "status": reservation.status,
                "check_in": reservation.check_in,
                'check_out': reservation.check_out,
                'created_at': reservation.created_at,
                'hotel': {
                    'id': reservation.hotel.id,
                    'name': reservation.hotel.name
                },
                'reserved_room_types': [
                    {
                        'name': reserved_room_type.room_type.name,
                        'quantity': reserved_room_type.nb_rooms
                    } for reserved_room_type in reservation.reserved_room_types.all()
                ]
            } for reservation in guest.reservations.all()
        ] if guest.reservations.count() > 0 else None

    class Meta:
        model = Guest
        fields = ['role', 'first_name', 'last_name', 'birthday', 'email', 'phone', 'about', 'profile_pic',
                  'overall_rating', 'address', 'country', 'reservations']


class GuestTokensSerializer(DataclassSerializer):
    class Meta:
        dataclass = GuestTokens


class EssentialGuestInfoSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    def get_email(self, guest: Guest):
        return guest.user.email

    class Meta:
        model = Guest
        fields = ['id', 'first_name', 'last_name', 'profile_pic', 'email']


class GuestSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Guest
        fields = ['id', 'first_name', 'last_name', 'profile_pic', 'status', 'created_at', 'country']


class BaseGuestInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    birthday = serializers.DateField(required=False)
    about = serializers.CharField(max_length=255, required=False)
    address = serializers.CharField(max_length=255, required=False)
    country_code_id = serializers.IntegerField(required=False)
    phone = serializers.IntegerField(required=False, allow_null=True, validators=[RegexValidator(regex="^\d{7,15}$")])
    country_id = serializers.IntegerField(required=False)

    def validate_first_name(self, value):
        return escape(value)

    def validate_last_name(self, value):
        return escape(value)

    def validate_address(self, value):
        return escape(value)


class CreateGuestRequestSerializer(BaseGuestInfoSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)

    def validate_email(self, value):
        return escape(value)

    def validate_password(self, value):
        return escape(value)


class UpdateGuestFormSerializer(serializers.Serializer):
    body = serializers.JSONField()
    profile_pic = serializers.ImageField(required=False)

    def validate(self, data):
        serializer = BaseGuestInfoSerializer(data=data['body'])
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        return data
