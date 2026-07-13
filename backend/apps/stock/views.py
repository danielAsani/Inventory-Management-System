from .models import Magasin, Materiel, Consommable
from .serializers import MagasinSerializer, MaterielSerializer, ConsommableSerializer
from apps.core.permissions import (
    GESTION_WRITE_ROLES,
    READ_ALL_ROLES,
    ROLE_ADMIN,
    ROLE_GESTION,
    ROLE_MAGASIN,
    RoleBasedPermission,
)
from apps.organisation.models import Direction, Service
from apps.operations.models import Affectation
from django.db.models import Q
from rest_framework.filters import SearchFilter
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
        service_ids = Service.objects.filter(
            id_direction_id__in=direction_ids
        ).values_list("id_service", flat=True)
        perimeter_filter = Q(
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
                | Q(
                    affectations__entite_type=Affectation.EntiteType.SERVICE,
                    affectations__entite_id__in=service_ids,
                )
            )
        )

    elif scope_type == "DIRECTION" and user.id_direction_id:
        service_ids = Service.objects.filter(
            id_direction_id=user.id_direction_id
        ).values_list("id_service", flat=True)
        perimeter_filter = Q(id_magasin__id_service__id_direction_id=user.id_direction_id)
        affectation_filter = (
            Q(affectations__statut=Affectation.StatutAffectation.ACTIVE)
            & (
                Q(
                    affectations__entite_type=Affectation.EntiteType.DIRECTION,
                    affectations__entite_id=user.id_direction_id,
                )
                | Q(
                    affectations__entite_type=Affectation.EntiteType.SERVICE,
                    affectations__entite_id__in=service_ids,
                )
            )
        )

    elif scope_type == "SERVICE" and user.id_service_id:
        perimeter_filter = Q(id_magasin__id_service_id=user.id_service_id)
        affectation_filter = (
            Q(affectations__statut=Affectation.StatutAffectation.ACTIVE)
            & Q(
                affectations__entite_type=Affectation.EntiteType.SERVICE,
                affectations__entite_id=user.id_service_id,
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
        return queryset.filter(id_service__id_direction__id_departement_id=user.id_departement_id)

    if scope_type == "DIRECTION" and user.id_direction_id:
        return queryset.filter(id_service__id_direction_id=user.id_direction_id)

    if scope_type == "SERVICE" and user.id_service_id:
        return queryset.filter(id_service_id=user.id_service_id)

    if scope_type == "MAGASIN" and user.id_magasin_id:
        return queryset.filter(id_magasin_id=user.id_magasin_id)

    return queryset.none()


class MagasinViewset(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    queryset = Magasin.objects.all()
    serializer_class = MagasinSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_magasin", "nom_magasin", "description_localisation"]

    def get_queryset(self):
        return scoped_magasin_queryset(super().get_queryset(), self.request.user)


class MaterielViewset(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        'read': READ_ALL_ROLES,
        'create': GESTION_WRITE_ROLES,
        'update': GESTION_WRITE_ROLES,
        'partial_update': GESTION_WRITE_ROLES,
    }
    queryset = Materiel.objects.select_related(
        "id_magasin",
        "id_magasin__id_service",
        "id_magasin__id_service__id_direction",
        "id_magasin__id_service__id_direction__id_departement",
    ).all()
    serializer_class = MaterielSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_materiel", "numero_serie", "marque", "modele", "code_barre", "qr_code"]

    def get_queryset(self):
        return scoped_stock_queryset(
            super().get_queryset(),
            self.request.user,
            include_affectations=True,
        )


class ConsommableViewset(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    queryset = Consommable.objects.select_related(
        "id_magasin",
        "id_magasin__id_service",
        "id_magasin__id_service__id_direction",
        "id_magasin__id_service__id_direction__id_departement",
    ).all()
    serializer_class = ConsommableSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_consommable", "nom_consommable"]

    def get_queryset(self):
        return scoped_stock_queryset(super().get_queryset(), self.request.user)
