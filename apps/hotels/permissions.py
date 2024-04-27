from django.contrib.auth.models import Permission
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.has_owner_account()
        return False

    def has_object_permission(self, request, view, hotel):
        return request.user == hotel.owner.user


class IsGuest(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.has_guest_account()
        return False

    def has_object_permission(self, request, view, hotel):
        return request.user == hotel.guest.user
