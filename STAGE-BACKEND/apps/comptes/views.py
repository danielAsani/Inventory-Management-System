from rest_framework.viewsets import ModelViewSet
from apps.core.cache import CACHE_LONG, CachedListRetrieveMixin
from apps.core.permissions import RoleBasedPermission

from .models import Role, Users
from .serializers import RoleSerializer, UsersSerializer


class RoleViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    cache_timeout = CACHE_LONG
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UsersViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
