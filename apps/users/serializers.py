from django.contrib.auth.password_validation import MinimumLengthValidator
from rest_framework import serializers as rest_serializers
from rest_framework.exceptions import ValidationError

from apps.guests.models import Guest


class SignupRequestSerializer(rest_serializers.Serializer):
    email = rest_serializers.CharField(max_length=255, required=True)
    password = rest_serializers.CharField(max_length=255, required=True)
    confirm_password = rest_serializers.CharField(max_length=255, required=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError(detail={'detail': 'passwords are not identical'})
        return attrs


class ProfileSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'birthday', 'profile_pic']


class TokensSerializer(rest_serializers.Serializer):
    access = rest_serializers.CharField(max_length=255)
    refresh = rest_serializers.CharField(max_length=255)


class EmailSerializer(rest_serializers.Serializer):
    email = rest_serializers.EmailField()


class ConfirmationCodeRequestSerializer(rest_serializers.Serializer):
    email = rest_serializers.EmailField()
    confirmation_code = rest_serializers.IntegerField()


class CompletePasswordResetRequestSerializer(rest_serializers.Serializer):
    token = rest_serializers.UUIDField()
    new_password = rest_serializers.CharField(max_length=255)


class LoginAdminRequestSerializer(rest_serializers.Serializer):
    email = rest_serializers.CharField(max_length=255)
    password = rest_serializers.CharField(max_length=255)
