from .models import Magasin, Materiel, Consommable
from .serializers import MagasinSerializer, MaterielSerializer, ConsommableSerializer
from apps.core.filters import parse_bool
from apps.core.permissions import (
    READ_ALL_ROLES,
    ROLE_ADMIN,
    ROLE_GESTION,
    ROLE_MAGASIN,
    RoleBasedPermission,
)
from apps.core.deletion import CascadeProtectedDeleteMixin
from apps.organisation.models import Direction
from apps.operations.models import Affectation
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


def scoped_stock_queryset(queryset, user, include_affectations=False):
    role = getattr(user, "role_code", None)
    scope_type = getattr(user, "scope_type", None)

    if role == ROLE_ADMIN:
        return queryset

    if role == ROLE_MAGASIN:
        if scope_type == "GENERAL":
            return queryset
        if scope_type == "MAGASIN" and user.id_magasin_id:
            return queryset.filter(id_magasin_id=user.id_magasin_id)
        return queryset.none()

    if role != ROLE_GESTION:
        return queryset.none()

    if scope_type == "GENERAL":
        return queryset.none()

    perimeter_filter = Q()
    affectation_filter = Q()

    if scope_type == "DEPARTEMENT" and user.id_departement_id:
        direction_ids = Direction.objects.filter(
            id_departement_id=user.id_departement_id
        ).values_list("id_direction", flat=True)
        perimeter_filter = Q(
            id_magasin__id_direction__id_departement_id=user.id_departement_id
        ) | Q(
            id_magasin__id_service__id_direction__id_departement_id=user.id_departement_id
        )
        affectation_filter = (
            Q(affectations__statut=Affectation.StatutAffectation.ACTIVE)
            & (
                Q(
                    affectations__entite_type=Affectation.EntiteType.DEPARTEMENT,
                    affectations__entite_id=user.id_departement_id,
                )
                | Q(
                    affectations__entite_type=Affectation.EntiteType.DIRECTION,
                    affectations__entite_id__in=direction_ids,
                )
            )
        )

    elif scope_type == "DIRECTION" and user.id_direction_id:
        perimeter_filter = Q(id_magasin__id_direction_id=user.id_direction_id) | Q(
            id_magasin__id_service__id_direction_id=user.id_direction_id
        )
        affectation_filter = (
            Q(affectations__statut=Affectation.StatutAffectation.ACTIVE)
            & (
                Q(
                    affectations__entite_type=Affectation.EntiteType.DIRECTION,
                    affectations__entite_id=user.id_direction_id,
                )
            )
        )

    elif scope_type == "MAGASIN" and user.id_magasin_id:
        perimeter_filter = Q(id_magasin_id=user.id_magasin_id)

    if not perimeter_filter:
        return queryset.none()

    if include_affectations:
        return queryset.filter(perimeter_filter | affectation_filter).distinct()

    return queryset.filter(perimeter_filter).distinct()


def scoped_magasin_queryset(queryset, user):
    role = getattr(user, "role_code", None)
    scope_type = getattr(user, "scope_type", None)

    if role == ROLE_ADMIN:
        return queryset

    if role == ROLE_MAGASIN:
        if scope_type == "GENERAL":
            return queryset
        if scope_type == "MAGASIN" and user.id_magasin_id:
            return queryset.filter(id_magasin_id=user.id_magasin_id)
        return queryset.none()

    if role != ROLE_GESTION:
        return queryset.none()

    if scope_type == "GENERAL":
        return queryset.none()

    if scope_type == "DEPARTEMENT" and user.id_departement_id:
        return queryset.filter(
            Q(id_direction__id_departement_id=user.id_departement_id)
            | Q(id_service__id_direction__id_departement_id=user.id_departement_id)
        )

    if scope_type == "DIRECTION" and user.id_direction_id:
        return queryset.filter(
            Q(id_direction_id=user.id_direction_id)
            | Q(id_service__id_direction_id=user.id_direction_id)
        )

    if scope_type == "MAGASIN" and user.id_magasin_id:
        return queryset.filter(id_magasin_id=user.id_magasin_id)

    return queryset.none()


class MagasinViewset(CascadeProtectedDeleteMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    queryset = Magasin.objects.select_related(
        "id_direction",
        "id_direction__id_departement",
        "id_service",
        "id_service__id_direction",
        "id_service__id_direction__id_departement",
    ).all()
    serializer_class = MagasinSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_magasin", "nom_magasin", "description_localisation"]

    def get_queryset(self):
        queryset = scoped_magasin_queryset(super().get_queryset(), self.request.user)
        statut = parse_bool(self.request.query_params.get("statut"))
        if statut is not None:
            queryset = queryset.filter(statut=statut)
        return queryset


class MaterielViewset(CascadeProtectedDeleteMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        'read': READ_ALL_ROLES,
        'create': {ROLE_ADMIN},
        'update': {ROLE_ADMIN},
        'partial_update': {ROLE_ADMIN},
        'marquer_en_panne': {ROLE_ADMIN},
        'marquer_en_reparation': {ROLE_ADMIN},
        'marquer_hors_service': {ROLE_ADMIN},
    }
    queryset = Materiel.objects.select_related(
        "id_magasin",
        "id_magasin__id_direction",
        "id_magasin__id_direction__id_departement",
        "id_magasin__id_service",
        "id_magasin__id_service__id_direction",
        "id_magasin__id_service__id_direction__id_departement",
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
    role_permissions = {'read': READ_ALL_ROLES}
    queryset = Consommable.objects.select_related(
        "id_magasin",
        "id_magasin__id_direction",
        "id_magasin__id_direction__id_departement",
        "id_magasin__id_service",
        "id_magasin__id_service__id_direction",
        "id_magasin__id_service__id_direction__id_departement",
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
