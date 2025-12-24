from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Analysts can only read.
    """

    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Allow write operations only for admins
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsAnalystOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow analysts and admins to read alerts.
    Only admins can modify.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow write operations only for admins
        return request.user.is_admin()
