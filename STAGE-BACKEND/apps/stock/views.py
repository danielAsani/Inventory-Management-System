from .models import Magasin, Materiel, Consommable
from .serializers import MagasinSerializer, MaterielSerializer, ConsommableSerializer
from apps.core.cache import CACHE_MEDIUM, CachedListRetrieveMixin
from apps.core.permissions import GESTIONNAIRE_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from rest_framework.viewsets import ModelViewSet


class MagasinViewset(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer

class MaterielViewset(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTIONNAIRE_WRITE_ROLES, 'update': GESTIONNAIRE_WRITE_ROLES, 'partial_update': GESTIONNAIRE_WRITE_ROLES}
    queryset = Materiel.objects.all()
    serializer_class = MaterielSerializer

class ConsommableViewset(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    queryset = Consommable.objects.all()
    serializer_class = ConsommableSerializer
