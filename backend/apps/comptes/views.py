from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from apps.core.cache import CACHE_LONG, CachedListRetrieveMixin
from apps.core.filters import parse_bool
from apps.core.permissions import RoleBasedPermission

from .models import Role, Users
from .serializers import RoleSerializer, UsersSerializer


class RoleViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    auditor_read_allowed = False
    cache_timeout = CACHE_LONG
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_role", "nom_role", "description"]

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = parse_bool(self.request.query_params.get("statut"))
        if statut is not None:
            queryset = queryset.filter(statut=statut)
        return queryset


class UsersViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    auditor_read_allowed = False
    queryset = Users.objects.select_related(
        "id_role",
        "id_departement",
        "id_direction",
    )
    serializer_class = UsersSerializer
    filter_backends = [SearchFilter]
    search_fields = ["nom_users", "matricule", "email", "telephone"]

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = parse_bool(self.request.query_params.get("is_active"))
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset
