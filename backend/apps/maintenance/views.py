from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from apps.core.deletion import CascadeProtectedDeleteMixin
from apps.core.permissions import READ_ALL_ROLES, ROLE_ADMIN, ROLE_GESTION, ROLE_MAGASIN, RoleBasedPermission
from .models import Entretien, Reparation
from .serializers import EntretienSerializer, ReparationSerializer


class EntretienViewSet(CascadeProtectedDeleteMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        'read': READ_ALL_ROLES,
        'create': {ROLE_ADMIN, ROLE_GESTION},
        'update': {ROLE_ADMIN, ROLE_MAGASIN},
        'partial_update': {ROLE_ADMIN, ROLE_MAGASIN},
    }
    queryset = Entretien.objects.select_related(
        "id_materiel",
        "id_materiel__id_categorie",
        "id_materiel__id_categorie__id_famille",
    ).all()
    serializer_class = EntretienSerializer
    filter_backends = [SearchFilter]
    search_fields = ["type_entretien", "type_prestataire", "nom_prestataire", "statut", "description", "observation"]

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = self.request.query_params.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset


class ReparationViewSet(CascadeProtectedDeleteMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': {ROLE_ADMIN}, 'update': {ROLE_ADMIN}, 'partial_update': {ROLE_ADMIN}}
    queryset = Reparation.objects.select_related(
        "id_materiel",
        "id_materiel__id_categorie",
        "id_materiel__id_categorie__id_famille",
    ).all()
    serializer_class = ReparationSerializer
    filter_backends = [SearchFilter]
    search_fields = ["type_prestataire", "nom_prestataire", "statut", "description", "observation"]

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = self.request.query_params.get("statut")
        if statut:
            queryset = queryset.filter(statut=statut)
        return queryset

    def _sync_materiel_state(self, reparation):
        materiel = reparation.id_materiel
        if reparation.statut == Reparation.StatutReparation.EN_ATTENTE:
            materiel.etat = materiel.EtatMateriel.EN_PANNE
        elif reparation.statut == Reparation.StatutReparation.EN_COURS:
            materiel.etat = materiel.EtatMateriel.EN_REPARATION
        elif reparation.statut == Reparation.StatutReparation.TERMINEE:
            materiel.etat = materiel.EtatMateriel.BON
        elif reparation.statut == Reparation.StatutReparation.ANNULEE:
            materiel.etat = materiel.EtatMateriel.EN_PANNE
        materiel.save(update_fields=["etat"])

    def perform_create(self, serializer):
        reparation = serializer.save()
        self._sync_materiel_state(reparation)

    def perform_update(self, serializer):
        reparation = serializer.save()
        self._sync_materiel_state(reparation)
