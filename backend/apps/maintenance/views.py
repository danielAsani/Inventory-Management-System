from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import GESTION_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Entretien, Reparation
from .serializers import EntretienSerializer, ReparationSerializer


class EntretienViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTION_WRITE_ROLES, 'update': GESTION_WRITE_ROLES, 'partial_update': GESTION_WRITE_ROLES}
    queryset = Entretien.objects.all()
    serializer_class = EntretienSerializer
    filter_backends = [SearchFilter]
    search_fields = ["type_entretien", "type_prestataire", "nom_prestataire", "statut", "description", "observation"]


class ReparationViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTION_WRITE_ROLES, 'update': GESTION_WRITE_ROLES, 'partial_update': GESTION_WRITE_ROLES}
    queryset = Reparation.objects.all()
    serializer_class = ReparationSerializer
    filter_backends = [SearchFilter]
    search_fields = ["type_prestataire", "nom_prestataire", "statut", "description", "observation"]
