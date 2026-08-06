from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.deletion import CascadeProtectedDeleteMixin
from apps.core.filters import parse_bool
from apps.core.permissions import (
    READ_ALL_ROLES,
    ROLE_ADMIN,
    RoleBasedPermission,
)
from .models import Consommable, Materiel
from .serializers import ConsommableSerializer, MaterielSerializer


def scoped_stock_queryset(queryset, user, include_affectations=False):
    role = getattr(user, "role_code", None)
    if role in READ_ALL_ROLES:
        return queryset.distinct() if include_affectations else queryset
    return queryset.none()


class MaterielViewset(CascadeProtectedDeleteMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "read": READ_ALL_ROLES,
        "create": {ROLE_ADMIN},
        "update": {ROLE_ADMIN},
        "partial_update": {ROLE_ADMIN},
        "marquer_en_panne": {ROLE_ADMIN},
        "marquer_en_reparation": {ROLE_ADMIN},
        "marquer_hors_service": {ROLE_ADMIN},
    }
    queryset = Materiel.objects.select_related(
        "id_categorie",
        "id_categorie__id_famille",
        "id_fournisseur",
    ).all()
    serializer_class = MaterielSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_materiel", "numero_serie", "marque", "modele", "code_barre", "qr_code"]

    def get_queryset(self):
        queryset = scoped_stock_queryset(
            super().get_queryset(),
            self.request.user,
            include_affectations=True,
        )
        etat = self.request.query_params.get("etat")
        statut_stock = self.request.query_params.get("statut_stock")
        id_categorie = self.request.query_params.get("id_categorie")
        if etat:
            queryset = queryset.filter(etat=etat)
        if statut_stock:
            queryset = queryset.filter(statut_stock=statut_stock)
        if id_categorie:
            queryset = queryset.filter(id_categorie_id=id_categorie)
        return queryset

    def _set_etat(self, etat):
        materiel = self.get_object()
        materiel.etat = etat
        materiel.save(update_fields=["etat"])
        return Response(self.get_serializer(materiel).data)

    @action(detail=True, methods=["post"], url_path="marquer-en-panne")
    def marquer_en_panne(self, request, pk=None):
        return self._set_etat(Materiel.EtatMateriel.EN_PANNE)

    @action(detail=True, methods=["post"], url_path="marquer-en-reparation")
    def marquer_en_reparation(self, request, pk=None):
        return self._set_etat(Materiel.EtatMateriel.EN_REPARATION)

    @action(detail=True, methods=["post"], url_path="marquer-hors-service")
    def marquer_hors_service(self, request, pk=None):
        return self._set_etat(Materiel.EtatMateriel.HORS_SERVICE)


class ConsommableViewset(CascadeProtectedDeleteMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {"read": READ_ALL_ROLES}
    queryset = Consommable.objects.select_related(
        "id_categorie",
        "id_categorie__id_famille",
        "id_unite",
    ).all()
    serializer_class = ConsommableSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_consommable", "nom_consommable"]

    def get_queryset(self):
        queryset = scoped_stock_queryset(super().get_queryset(), self.request.user)
        statut = parse_bool(self.request.query_params.get("statut"))
        id_categorie = self.request.query_params.get("id_categorie")
        if statut is not None:
            queryset = queryset.filter(statut=statut)
        if id_categorie:
            queryset = queryset.filter(id_categorie_id=id_categorie)
        return queryset
