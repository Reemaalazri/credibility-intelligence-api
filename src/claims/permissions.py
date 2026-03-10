from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Allow access if the user owns the report or is staff/admin.
    """

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or obj.user == request.user
        )