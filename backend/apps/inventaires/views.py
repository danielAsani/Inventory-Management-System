from rest_framework.filters import SearchFilter
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from apps.core.deletion import CascadeProtectedDeleteMixin
from apps.core.permissions import ROLE_ADMIN, ROLE_MAGASIN, RoleBasedPermission
from .models import Inventaire, InventaireDetail
from .serializers import InventaireDetailSerializer, InventaireSerializer


class InventaireViewSet(CascadeProtectedDeleteMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        'read': {ROLE_ADMIN, ROLE_MAGASIN},
        'create': {ROLE_ADMIN, ROLE_MAGASIN},
        'update': {ROLE_ADMIN, ROLE_MAGASIN},
        'partial_update': {ROLE_ADMIN, ROLE_MAGASIN},
        'destroy': {ROLE_ADMIN, ROLE_MAGASIN},
    }
    queryset = Inventaire.objects.select_related("effectue_par", "cree_par").prefetch_related(
        "details",
        "details__id_materiel",
        "details__id_consommable",
    ).all()
    serializer_class = InventaireSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_inventaire", "entite_type", "type_inventaire", "statut", "observation"]

    def get_queryset(self):
        self._ensure_inventory_access()
        queryset = super().get_queryset()
        statut = self.request.query_params.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset

    def perform_create(self, serializer):
        self._ensure_inventory_access()
        serializer.save(cree_par=self.request.user)

    def perform_update(self, serializer):
        self._ensure_inventory_access()
        serializer.save()

    def _ensure_inventory_access(self):
        user = self.request.user
        if user.role_code == ROLE_ADMIN:
            return
        if user.role_code == ROLE_MAGASIN and user.scope_type == "GENERAL":
            return
        raise PermissionDenied("Seul le magasinier general peut acceder aux inventaires.")


class InventaireDetailViewSet(CascadeProtectedDeleteMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        'read': {ROLE_ADMIN, ROLE_MAGASIN},
        'create': {ROLE_ADMIN, ROLE_MAGASIN},
        'update': {ROLE_ADMIN, ROLE_MAGASIN},
        'partial_update': {ROLE_ADMIN, ROLE_MAGASIN},
        'destroy': {ROLE_ADMIN, ROLE_MAGASIN},
    }
    queryset = InventaireDetail.objects.select_related(
        "id_inventaire",
        "id_materiel",
        "id_materiel__id_categorie",
        "id_materiel__id_categorie__id_famille",
        "id_consommable",
        "id_consommable__id_categorie",
        "id_consommable__id_categorie__id_famille",
    ).all()
    serializer_class = InventaireDetailSerializer
    filter_backends = [SearchFilter]
    search_fields = ["observation"]

    def get_queryset(self):
        self._ensure_inventory_access()
        queryset = super().get_queryset()
        id_inventaire = self.request.query_params.get("id_inventaire")
        if id_inventaire:
            queryset = queryset.filter(id_inventaire_id=id_inventaire)
        return queryset

    def perform_create(self, serializer):
        self._ensure_inventory_access()
        serializer.save()

    def perform_update(self, serializer):
        self._ensure_inventory_access()
        serializer.save()

    def _ensure_inventory_access(self):
        user = self.request.user
        if user.role_code == ROLE_ADMIN:
            return
        if user.role_code == ROLE_MAGASIN and user.scope_type == "GENERAL":
            return
        raise PermissionDenied("Seul le magasinier general peut acceder aux lignes d'inventaire.")
