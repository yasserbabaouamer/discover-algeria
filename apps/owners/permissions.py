from rest_framework.permissions import BasePermission

from apps.owners.models import Owner


class IsOwner(BasePermission):

    def has_permission(self, request, view):
        return request.user.has_owner_account()

    def has_object_permission(self, request, view, owner: Owner):
        return request.user == owner.user
