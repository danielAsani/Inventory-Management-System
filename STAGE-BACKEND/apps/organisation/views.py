from rest_framework.viewsets import ModelViewSet
from apps.core.cache import CACHE_LONG, CachedListRetrieveMixin
from apps.core.permissions import READ_ALL_ROLES, RoleBasedPermission
from .models import Departement, Direction, Service
from .serializers import (
    DepartementSerializer,
    DirectionSerializer,
    ServiceSerializer,
)


class DepartementViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_LONG
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer


class DirectionViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_LONG
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer


class ServiceViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_LONG
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
