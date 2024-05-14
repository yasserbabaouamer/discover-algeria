from rest_framework import serializers
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


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    overall_rating = serializers.FloatField()
    country = CountrySerializer()

    def get_email(self, guest: Guest):
        return guest.user.email

    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'birthday', 'email', 'phone', 'about',
                  'overall_rating', 'address', 'country', 'profile_pic']


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
