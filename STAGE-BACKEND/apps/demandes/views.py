from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import GESTIONNAIRE_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Demande
from .serializers import DemandeSerializer


class DemandeViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTIONNAIRE_WRITE_ROLES, 'update': GESTIONNAIRE_WRITE_ROLES, 'partial_update': GESTIONNAIRE_WRITE_ROLES}
    queryset = Demande.objects.all()
    serializer_class = DemandeSerializer
