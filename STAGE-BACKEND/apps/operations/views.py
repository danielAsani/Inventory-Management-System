from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import GESTIONNAIRE_WRITE_ROLES, MAGASINIER_CREATE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Affectation, Consommation, MouvementStock
from .serializers import AffectationSerializer, ConsommationSerializer, MouvementStockSerializer


class MouvementStockViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': MAGASINIER_CREATE_ROLES}
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer


class AffectationViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTIONNAIRE_WRITE_ROLES, 'update': GESTIONNAIRE_WRITE_ROLES, 'partial_update': GESTIONNAIRE_WRITE_ROLES}
    queryset = Affectation.objects.all()
    serializer_class = AffectationSerializer


class ConsommationViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': MAGASINIER_CREATE_ROLES}
    queryset = Consommation.objects.all()
    serializer_class = ConsommationSerializer
