import datetime

from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework_dataclasses.serializers import DataclassSerializer

from .dtos import *
from .models import Owner


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


class OwnerEssentialsInfo(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    def get_email(self, owner: Owner):
        return owner.user.email

    class Meta:
        model = Owner
        fields = ['id', 'first_name', 'last_name', 'profile_pic', 'email']
