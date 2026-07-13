from rest_framework.filters import SearchFilter
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
    queryset = Departement.objects.filter(statut=True)
    serializer_class = DepartementSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_departement", "nom_departement", "abreviation"]


class DirectionViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_LONG
    queryset = Direction.objects.filter(statut=True, id_departement__statut=True)
    serializer_class = DirectionSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_direction", "nom_direction", "abreviation"]


class ServiceViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_LONG
    queryset = Service.objects.filter(statut=True, id_direction__statut=True, id_direction__id_departement__statut=True)
    serializer_class = ServiceSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_service", "nom_service", "abreviation"]
