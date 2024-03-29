from rest_framework import permissions


class IsAdminOrOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.is_staff
                or obj.author == request.user
            )
        )
