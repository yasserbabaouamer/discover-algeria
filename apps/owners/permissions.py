from rest_framework.permissions import BasePermission

from apps.owners.models import Owner


class IsOwnerOrAdmin(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.has_owner_account() or request.user.is_superuser
        return False

    def has_object_permission(self, request, view, owner: Owner):
        if request.user.is_superuser:
            return True
        return request.user == owner.user
