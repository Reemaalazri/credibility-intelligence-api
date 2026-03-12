from rest_framework.permissions import BasePermission


# Custom permission:
# only the report owner or an admin can access/modify the object
class IsOwnerOrAdmin(BasePermission):
    """
    Allow access if the user owns the report or is staff/admin.
    """

    # Check user is authenticated and either:
    # - an admin/staff user
    # - the owner of the report
    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or obj.user == request.user
        )
