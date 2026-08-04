from rest_framework.filters import SearchFilter
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import MAGASIN_WRITE_ROLES, OPERATION_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Affectation, Consommation, MouvementStock
from .serializers import AffectationSerializer, ConsommationSerializer, MouvementStockSerializer


class MouvementStockViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': OPERATION_WRITE_ROLES}
    queryset = MouvementStock.objects.select_related(
        "id_materiel",
        "id_consommable",
        "magasin_source",
        "magasin_destination",
        "fait_par",
    ).all()
    serializer_class = MouvementStockSerializer
    filter_backends = [SearchFilter]
    search_fields = ["type_mouvement", "reference_document", "observation"]

    def get_queryset(self):
        queryset = super().get_queryset()
        type_mouvement = self.request.query_params.get("type_mouvement")
        if type_mouvement:
            queryset = queryset.filter(type_mouvement=type_mouvement)
        return queryset

    def perform_create(self, serializer):
        serializer.save(fait_par=self.request.user)

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE", detail="Un mouvement de stock ne peut pas etre supprime.")


class AffectationViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        'read': READ_ALL_ROLES,
        'create': MAGASIN_WRITE_ROLES,
        'update': MAGASIN_WRITE_ROLES,
        'partial_update': MAGASIN_WRITE_ROLES,
    }
    queryset = Affectation.objects.select_related(
        "id_materiel",
        "agent_id_departement",
        "agent_id_direction",
    ).all()
    serializer_class = AffectationSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_affectation", "code_barre", "qr_code", "entite_type", "statut", "observation"]

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = self.request.query_params.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE", detail="Une affectation ne peut pas etre supprimee.")


class ConsommationViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': OPERATION_WRITE_ROLES}
    queryset = Consommation.objects.select_related(
        "id_consommable",
        "id_consommable__id_categorie",
        "id_consommable__id_categorie__id_famille",
        "id_departement",
        "id_direction",
        "fait_par",
    ).all()
    serializer_class = ConsommationSerializer
    filter_backends = [SearchFilter]
    search_fields = [
        "demandeur",
        "observation",
        "destination_type",
        "id_departement__nom_departement",
        "id_direction__nom_direction",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        id_consommable = self.request.query_params.get("id_consommable")
        if id_consommable:
            queryset = queryset.filter(id_consommable_id=id_consommable)
        return queryset

    def perform_create(self, serializer):
        serializer.save(fait_par=self.request.user)

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE", detail="Une consommation ne peut pas etre supprimee.")
