from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import GESTION_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Inventaire, InventaireDetail
from .serializers import InventaireDetailSerializer, InventaireSerializer


class InventaireViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTION_WRITE_ROLES, 'update': GESTION_WRITE_ROLES, 'partial_update': GESTION_WRITE_ROLES}
    queryset = Inventaire.objects.all()
    serializer_class = InventaireSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_inventaire", "entite_type", "type_inventaire", "statut", "observation"]


class InventaireDetailViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTION_WRITE_ROLES, 'update': GESTION_WRITE_ROLES, 'partial_update': GESTION_WRITE_ROLES}
    queryset = InventaireDetail.objects.all()
    serializer_class = InventaireDetailSerializer
    filter_backends = [SearchFilter]
    search_fields = ["observation"]
