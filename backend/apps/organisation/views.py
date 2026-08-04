from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from apps.core.cache import CACHE_LONG, CachedListRetrieveMixin
from apps.core.filters import parse_bool
from apps.core.permissions import READ_ALL_ROLES, RoleBasedPermission
from .models import Departement, Direction
from .serializers import (
    DepartementSerializer,
    DirectionSerializer,
)


class DepartementViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_LONG
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_departement", "nom_departement", "abreviation"]

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = parse_bool(self.request.query_params.get("statut"))
        if statut is not None:
            queryset = queryset.filter(statut=statut)
        return queryset


class DirectionViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_LONG
    queryset = Direction.objects.select_related("id_departement").all()
    serializer_class = DirectionSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_direction", "nom_direction", "abreviation"]

    def get_queryset(self):
        queryset = super().get_queryset()
        id_departement = self.request.query_params.get("id_departement")
        statut = parse_bool(self.request.query_params.get("statut"))
        if id_departement:
            queryset = queryset.filter(id_departement_id=id_departement)
        if statut is not None:
            queryset = queryset.filter(statut=statut)
        return queryset
