from rest_framework import permissions


class IsVerified(permissions.BasePermission):
    """
    Allows access only to verified users (is_verified=True).
    Typically applied to sensitive endpoints like AI chat, payments, etc.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'is_verified', False) is True
        )


class IsBroker(permissions.BasePermission):
    """
    Allows access only to users with the 'broker' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'broker')


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Admin can edit, others can only read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')
