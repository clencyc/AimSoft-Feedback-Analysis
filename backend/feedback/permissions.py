from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """Allow access only to Django superusers."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_superuser)
