from django.contrib.auth.models import Permission
from rest_framework import permissions

from apps.hotels import services


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.has_owner_account()
        return False

    def has_object_permission(self, request, view, hotel):
        return request.user == hotel.owner.user


class IsGuestOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.has_guest_account() or request.user.is_superuser
        return False

    def has_object_permission(self, request, view, guest):
        if request.user.is_superuser:
            return True
        return request.user.guest == guest
