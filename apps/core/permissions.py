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


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object or admins to edit/delete it.
    Works with objects that have `user`, `owner`, or `broker` relations.
    """
    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin':
            return True

        # Direct user owner (e.g., Favorite, VisitRequest, BrokerProfile)
        owner = getattr(obj, 'user', None) or getattr(obj, 'owner', None)
        if owner is not None:
            return bool(request.user and request.user.is_authenticated and request.user == owner)

        # Broker-owned objects (e.g., Property -> broker -> user)
        broker = getattr(obj, 'broker', None)
        if broker is not None:
            broker_user = getattr(broker, 'user', None)
            return bool(request.user and request.user.is_authenticated and broker_user and request.user == broker_user)

        return False
