from rest_framework import serializers as rest_serializers
from rest_framework.exceptions import ValidationError

from apps.guests.models import Guest


class GuestLoginRequestSerializer(rest_serializers.Serializer):
    email = rest_serializers.CharField(max_length=255, required=True)
    password = rest_serializers.CharField(max_length=255, required=True)


class GuestSignupRequestSerializer(rest_serializers.Serializer):
    email = rest_serializers.CharField(max_length=255, required=True)
    password = rest_serializers.CharField(max_length=255, required=True)
    confirm_password = rest_serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError(detail={'detail': 'passwords are not identical'})
        return attrs


class ConfirmationRequestSerializer(rest_serializers.Serializer):
    token = rest_serializers.UUIDField()
    confirmation_code = rest_serializers.IntegerField()


class ResendConfirmationRequestSerializer(rest_serializers.Serializer):
    token = rest_serializers.UUIDField()


class QuickProfileRequestSerializer(rest_serializers.Serializer):
    first_name = rest_serializers.CharField(max_length=255)
    last_name = rest_serializers.CharField(max_length=255)
    profile_pic = rest_serializers.ImageField()


class ProfileSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'birthday', 'profile_pic']


class TokensSerializer(rest_serializers.Serializer):
    access = rest_serializers.CharField(max_length=255)
    refresh = rest_serializers.CharField(max_length=255)
    has_guest_acc = rest_serializers.BooleanField()


class EmailSerializer(rest_serializers.Serializer):
    email = rest_serializers.EmailField()
