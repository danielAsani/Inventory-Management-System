from rest_framework.filters import SearchFilter
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import GESTION_WRITE_ROLES, OPERATION_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Affectation, Consommation, MouvementStock
from .serializers import AffectationSerializer, ConsommationSerializer, MouvementStockSerializer


class MouvementStockViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': OPERATION_WRITE_ROLES}
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer
    filter_backends = [SearchFilter]
    search_fields = ["type_mouvement", "reference_document", "observation"]

    def perform_create(self, serializer):
        serializer.save(fait_par=self.request.user)

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE", detail="Un mouvement de stock ne peut pas etre supprime.")


class AffectationViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTION_WRITE_ROLES, 'update': GESTION_WRITE_ROLES, 'partial_update': GESTION_WRITE_ROLES}
    queryset = Affectation.objects.all()
    serializer_class = AffectationSerializer
    filter_backends = [SearchFilter]
    search_fields = ["entite_type", "statut", "observation"]

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE", detail="Une affectation ne peut pas etre supprimee.")


class ConsommationViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': OPERATION_WRITE_ROLES}
    queryset = Consommation.objects.all()
    serializer_class = ConsommationSerializer
    filter_backends = [SearchFilter]
    search_fields = ["demandeur", "observation"]

    def perform_create(self, serializer):
        serializer.save(fait_par=self.request.user)

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE", detail="Une consommation ne peut pas etre supprimee.")
