from rest_framework import serializers

from apps.guests.models import Guest


class GuestLoginRequestSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)


class QuickProfileRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    profile_pic = serializers.ImageField(required=False)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'birthday', 'profile_pic']


class TokensSerializer(serializers.Serializer):
    access = serializers.CharField(max_length=255)
    refresh = serializers.CharField(max_length=255)
    has_guest_acc = serializers.BooleanField()


class EssentialGuestInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id', 'first_name', 'last_name', 'profile_pic']
