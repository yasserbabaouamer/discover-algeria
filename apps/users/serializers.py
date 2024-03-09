from jsonschema.exceptions import ValidationError
from rest_framework import serializers as rest_serializers
from rest_framework.exceptions import ValidationError


class GuestLoginRequestSerializer(rest_serializers.Serializer):
    email = rest_serializers.CharField(max_length=255, required=True)
    password = rest_serializers.CharField(max_length=255, required=True)


class GuestSignupRequestSerializer(rest_serializers.Serializer):
    first_name = rest_serializers.CharField(max_length=255, required=True)
    last_name = rest_serializers.CharField(max_length=255, required=True)
    email = rest_serializers.CharField(max_length=255, required=True)
    password = rest_serializers.CharField(max_length=255, required=True)
    confirm_password = rest_serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError('passwords are not identical')
        return attrs


class TokensSerializer(rest_serializers.Serializer):
    access = rest_serializers.CharField(max_length=255)
    refresh = rest_serializers.CharField(max_length=255)
    is_activated = rest_serializers.BooleanField()


class ConfirmationRequestSerializer(rest_serializers.Serializer):
    confirmation_code = rest_serializers.IntegerField()
