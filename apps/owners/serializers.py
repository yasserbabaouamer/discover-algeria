import datetime

from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_dataclasses.serializers import DataclassSerializer
from django.utils.html import escape

from .dtos import *
from .models import Owner
from ..destinations.serializers import CountrySerializer


class OwnerLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)

    def validate(self, attrs):
        for key, value in attrs.items():
            attrs[key] = escape(value)
        return attrs


class OwnerTokensSerializer(DataclassSerializer):
    class Meta:
        dataclass = OwnerTokens


class SetupOwnerProfileFormSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    birthday = serializers.DateField()
    country_code_id = serializers.IntegerField()
    phone = serializers.IntegerField(validators=[RegexValidator(regex="^\d{7,15}$")])
    country_id = serializers.IntegerField()
    profile_pic = serializers.ImageField(required=False)

    def validate_birthday(self, value):
        if datetime.date.today() < value:
            raise serializers.ValidationError({'detail': f"{value} are you kidding me ?"})
        return value

    def validate_first_name(self, value):
        return escape(value)

    def validate_last_name(self, value):
        return escape(value)


class OwnerEssentialInfoSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    def get_phone(self, profile: Owner):
        return {
            'id': profile.country_code.id if profile.country_code is not None else None,
            'number': profile.phone,
            'code': profile.country_code.country_code if profile.country_code is not None else None,
            'flag': profile.country_code.flag.url if profile.country_code is not None else None
        }

    def get_email(self, owner: Owner):
        return owner.user.email

    class Meta:
        model = Owner
        fields = ['id', 'first_name', 'last_name', 'profile_pic', 'email', 'phone']


class OwnerProfileForAnyoneSerializer(OwnerEssentialInfoSerializer):
    country = CountrySerializer()
    overall_rating = serializers.FloatField()

    class Meta:
        model = Owner
        fields = list(OwnerEssentialInfoSerializer.Meta.fields
                      + ['about', 'overall_rating', 'country'])


class OwnerProfileSerializer(OwnerProfileForAnyoneSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, owner: Owner):
        return "owner"

    class Meta:
        model = Owner
        fields = OwnerProfileForAnyoneSerializer.Meta.fields + ['role', 'birthday', 'address']


class OwnerSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Owner
        fields = ['id', 'first_name', 'last_name', 'profile_pic', 'status', 'created_at', 'country']


class BaseOwnerSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    about = serializers.CharField(max_length=255, required=False)
    address = serializers.CharField(max_length=255, required=False)
    birthday = serializers.DateField(required=False)
    country_code_id = serializers.IntegerField(required=False)
    phone = serializers.IntegerField(required=False, allow_null=True, validators=[RegexValidator(regex="^\d{7,15}$")])
    country_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        for key, val in attrs.items():
            if not isinstance(val, str):
                continue
            attrs[key] = escape(val)
        return attrs


class CreateOwnerRequestSerializer(BaseOwnerSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)

    def validate_email(self, value):
        return escape(value)

    def validate_password(self, value):
        return escape(value)


class UpdateOwnerFormSerializer(serializers.Serializer):
    body = serializers.JSONField()
    profile_pic = serializers.ImageField(required=False)

    def validate(self, data):
        serializer = BaseOwnerSerializer(data=data['body'])
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)
        return data
