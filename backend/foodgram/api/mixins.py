from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .permissions import IsAdminOrOwner


class IsAdminOrOwnerMixin(viewsets.GenericViewSet):

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            permission_classes = [IsAdminOrOwner, ]
        else:
            permission_classes = [AllowAny, ]
        return [permission() for permission in permission_classes]
