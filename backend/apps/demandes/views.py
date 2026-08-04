from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.deletion import CascadeProtectedDeleteMixin
from apps.core.permissions import (
    GESTION_WRITE_ROLES,
    MAGASIN_WRITE_ROLES,
    READ_ALL_ROLES,
    ROLE_ADMIN,
    ROLE_GESTION,
    ROLE_MAGASIN,
    RoleBasedPermission,
)
from .models import Demande
from .serializers import DemandeSerializer


class DemandeViewSet(CascadeProtectedDeleteMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        "read": READ_ALL_ROLES,
        "create": GESTION_WRITE_ROLES,
        "update": GESTION_WRITE_ROLES,
        "partial_update": GESTION_WRITE_ROLES,
        "destroy": {ROLE_ADMIN},
        "valider_departement": GESTION_WRITE_ROLES,
        "rejeter_departement": GESTION_WRITE_ROLES,
        "finaliser_magasin": MAGASIN_WRITE_ROLES,
    }
    queryset = (
        Demande.objects.select_related(
            "id_departement",
            "id_direction_demandeuse",
            "id_demandeur",
            "id_validateur_departement",
            "id_magasinier_finalisateur",
            "id_materiel",
            "id_materiel__id_categorie",
            "id_consommable",
            "id_consommable__id_categorie",
        )
        .all()
    )
    serializer_class = DemandeSerializer
    filter_backends = [SearchFilter]
    search_fields = [
        "code_demande",
        "origine_type",
        "type_demande",
        "statut",
        "observation",
        "motif_rejet",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role_code in {ROLE_ADMIN, ROLE_MAGASIN}:
            return self._apply_filters(queryset)

        if user.role_code != ROLE_GESTION:
            return queryset.none()

        if user.scope_type == "DIRECTION" and user.id_direction_id:
            return self._apply_filters(queryset.filter(id_direction_demandeuse_id=user.id_direction_id))

        if user.scope_type == "DEPARTEMENT" and user.id_departement_id:
            return self._apply_filters(queryset.filter(id_departement_id=user.id_departement_id))

        if user.scope_type == "GENERAL":
            return self._apply_filters(queryset)

        return queryset.none()

    def _apply_filters(self, queryset):
        statut = self.request.query_params.get("statut")
        type_demande = self.request.query_params.get("type_demande")
        if statut:
            queryset = queryset.filter(statut=statut)
        if type_demande:
            queryset = queryset.filter(type_demande=type_demande)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        save_kwargs = {
            "id_demandeur": user,
            "statut": Demande.StatutDemande.EN_ATTENTE_DEPARTEMENT,
        }

        if user.role_code != ROLE_ADMIN:
            self._ensure_can_create_direction_request(user)
            direction = user.id_direction
            save_kwargs.update(
                {
                    "id_direction_demandeuse": direction,
                    "id_departement": direction.id_departement,
                    "origine_type": Demande.OrigineType.DIRECTION,
                    "origine_id": direction.id_direction,
                }
            )

        serializer.save(
            **save_kwargs
        )

    def perform_update(self, serializer):
        self._ensure_can_update_request(self.request.user, serializer.instance)
        serializer.save()

    @action(detail=True, methods=["post"], url_path="valider-departement")
    def valider_departement(self, request, pk=None):
        demande = self.get_object()
        self._ensure_can_validate_department(request.user, demande)

        if demande.statut != Demande.StatutDemande.EN_ATTENTE_DEPARTEMENT:
            raise ValidationError(
                {"statut": "Seule une demande en attente du departement peut etre validee."}
            )

        demande.statut = Demande.StatutDemande.EN_TRAITEMENT_MAGASIN
        demande.id_validateur_departement = request.user
        demande.date_validation_departement = timezone.now()
        demande.motif_rejet = None
        demande.save(
            update_fields=[
                "statut",
                "id_validateur_departement",
                "date_validation_departement",
                "motif_rejet",
            ]
        )
        return Response(self.get_serializer(demande).data)

    @action(detail=True, methods=["post"], url_path="rejeter-departement")
    def rejeter_departement(self, request, pk=None):
        demande = self.get_object()
        self._ensure_can_validate_department(request.user, demande)

        if demande.statut != Demande.StatutDemande.EN_ATTENTE_DEPARTEMENT:
            raise ValidationError(
                {"statut": "Seule une demande en attente du departement peut etre rejetee."}
            )

        motif = request.data.get("motif_rejet") or request.data.get("motif")
        if not motif:
            raise ValidationError({"motif_rejet": "Le motif de rejet est obligatoire."})

        demande.statut = Demande.StatutDemande.REJETEE
        demande.id_validateur_departement = request.user
        demande.date_validation_departement = timezone.now()
        demande.motif_rejet = motif
        demande.save(
            update_fields=[
                "statut",
                "id_validateur_departement",
                "date_validation_departement",
                "motif_rejet",
            ]
        )
        return Response(self.get_serializer(demande).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="finaliser-magasin")
    def finaliser_magasin(self, request, pk=None):
        demande = self.get_object()
        self._ensure_can_finalize_store(request.user)

        if demande.statut != Demande.StatutDemande.EN_TRAITEMENT_MAGASIN:
            raise ValidationError(
                {"statut": "Seule une demande envoyee au magasin peut etre finalisee."}
            )

        demande.statut = Demande.StatutDemande.TRAITEE
        demande.id_magasinier_finalisateur = request.user
        demande.date_finalisation = timezone.now()
        demande.save(
            update_fields=[
                "statut",
                "id_magasinier_finalisateur",
                "date_finalisation",
            ]
        )
        return Response(self.get_serializer(demande).data)

    def _ensure_can_validate_department(self, user, demande):
        if user.role_code == ROLE_ADMIN:
            return

        if user.scope_type != "DEPARTEMENT" or user.id_departement_id != demande.id_departement_id:
            raise PermissionDenied(
                "Seul un utilisateur du departement concerne peut valider cette demande."
            )

    def _ensure_can_create_direction_request(self, user):
        if user.role_code != ROLE_GESTION:
            raise PermissionDenied("Seul un utilisateur de direction peut creer une demande.")

        if user.scope_type != "DIRECTION" or not user.id_direction_id:
            raise PermissionDenied("Seul un utilisateur rattache a une direction peut creer une demande.")

    def _ensure_can_update_request(self, user, demande):
        if user.role_code == ROLE_ADMIN:
            return

        if demande.statut != Demande.StatutDemande.EN_ATTENTE_DEPARTEMENT:
            raise ValidationError(
                {"statut": "Seule une demande en attente du departement peut etre modifiee."}
            )

        if (
            user.role_code != ROLE_GESTION
            or user.scope_type != "DIRECTION"
            or user.id_direction_id != demande.id_direction_demandeuse_id
        ):
            raise PermissionDenied(
                "Seule la direction demandeuse peut modifier cette demande avant validation."
            )

    def _ensure_can_finalize_store(self, user):
        if user.role_code == ROLE_ADMIN:
            return

        if user.role_code != ROLE_MAGASIN or user.scope_type != "GENERAL":
            raise PermissionDenied("Seul le magasinier general peut finaliser cette demande.")
