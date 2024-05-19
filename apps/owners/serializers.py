import datetime

from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from .dtos import *
from .models import Owner
from ..destinations.serializers import CountrySerializer


class OwnerLoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)


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

    def validate(self, data):
        if datetime.date.today() < data['birthday']:
            raise serializers.ValidationError({'detail': f"{data['birthday']} are you kidding me ?"})
        return data


class OwnerEssentialInfoSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

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
        fields.remove('phone')


class OwnerProfileSerializer(OwnerProfileForAnyoneSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, owner: Owner):
        return "owner"

    class Meta:
        model = Owner
        fields = OwnerProfileForAnyoneSerializer.Meta.fields + ['role', 'birthday', 'phone', 'address']


class OwnerSerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Owner
        fields = ['id', 'first_name', 'last_name', 'profile_pic', 'status', 'created_at', 'country']
