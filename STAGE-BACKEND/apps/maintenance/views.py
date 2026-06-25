from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import GESTIONNAIRE_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Entretien, Reparation
from .serializers import EntretienSerializer, ReparationSerializer


class EntretienViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTIONNAIRE_WRITE_ROLES, 'update': GESTIONNAIRE_WRITE_ROLES, 'partial_update': GESTIONNAIRE_WRITE_ROLES}
    queryset = Entretien.objects.all()
    serializer_class = EntretienSerializer


class ReparationViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTIONNAIRE_WRITE_ROLES, 'update': GESTIONNAIRE_WRITE_ROLES, 'partial_update': GESTIONNAIRE_WRITE_ROLES}
    queryset = Reparation.objects.all()
    serializer_class = ReparationSerializer
