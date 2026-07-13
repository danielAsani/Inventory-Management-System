from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from apps.core.cache import CACHE_LONG, CachedListRetrieveMixin
from apps.core.permissions import RoleBasedPermission

from .models import Role, Users
from .serializers import RoleSerializer, UsersSerializer


class RoleViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    auditor_read_allowed = False
    cache_timeout = CACHE_LONG
    queryset = Role.objects.filter(statut=True)
    serializer_class = RoleSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_role", "nom_role", "description"]


class UsersViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    auditor_read_allowed = False
    queryset = Users.objects.filter(statut=True)
    serializer_class = UsersSerializer
    filter_backends = [SearchFilter]
    search_fields = ["nom_users", "matricule", "email", "telephone"]
