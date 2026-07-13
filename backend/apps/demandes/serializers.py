from rest_framework import serializers

from apps.comptes.models import Users
from apps.core.permissions import ROLE_ADMIN, ROLE_GESTION
from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_choice,
    validate_not_blank,
    validate_not_future,
    validate_positive,
)
from .models import Demande

DEMANDE_STATUTS = {
    "EN_ATTENTE_DEPARTEMENT",
    "EN_TRAITEMENT_MAGASIN",
    "REJETEE",
    "ANNULEE",
    "TRAITEE",
}
DEMANDE_TYPES = {"ACHAT", "REAPPROVISIONNEMENT", "REPARATION", "AUTRE"}


class DemandeSerializer(SanitizedModelSerializer):
    class Meta:
        model = Demande
        fields = "__all__"
        extra_kwargs = {
            "id_departement": {"required": False},
            "id_direction_demandeuse": {"required": False},
        }
        read_only_fields = [
            "id_demandeur",
            "id_validateur_departement",
            "date_validation_departement",
            "id_magasinier_finalisateur",
            "date_finalisation",
        ]

    def validate_code_demande(self, value):
        return validate_not_blank(value, "Le code de la demande ne peut pas etre vide.")

    def validate_type_demande(self, value):
        return validate_choice(
            value,
            DEMANDE_TYPES,
            "Le type de demande doit etre ACHAT, REAPPROVISIONNEMENT, REPARATION ou AUTRE.",
        )

    def validate_statut(self, value):
        return validate_choice(
            value,
            DEMANDE_STATUTS,
            "Le statut de la demande n'est pas valide.",
        )

    def validate_date_demande(self, value):
        return validate_not_future(value, "La date de demande ne peut pas etre dans le futur.")

    def validate_quantite_demandee(self, value):
        return validate_positive(value, "La quantite demandee doit etre superieure a 0.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance

        departement = attrs.get("id_departement") or getattr(instance, "id_departement", None)
        direction = attrs.get("id_direction_demandeuse") or getattr(
            instance, "id_direction_demandeuse", None
        )
        service = attrs.get("id_service_destinataire") or getattr(
            instance, "id_service_destinataire", None
        )
        type_demande = attrs.get("type_demande") or getattr(instance, "type_demande", None)
        materiel = attrs.get("id_materiel") or getattr(instance, "id_materiel", None)
        consommable = attrs.get("id_consommable") or getattr(instance, "id_consommable", None)
        quantite = attrs.get("quantite_demandee") or getattr(instance, "quantite_demandee", 1)
        request = self.context.get("request")
        user = getattr(request, "user", None)

        is_admin = user and getattr(user, "role_code", None) == ROLE_ADMIN

        if instance is None and is_admin and (not departement or not direction):
            raise serializers.ValidationError(
                {
                    "id_departement": "Le departement est obligatoire.",
                    "id_direction_demandeuse": "La direction demandeuse est obligatoire.",
                }
            )

        if instance is None and user and not is_admin:
            if (
                user.role_code != ROLE_GESTION
                or user.scope_type != Users.ScopeType.DIRECTION
                or not user.id_direction_id
            ):
                raise serializers.ValidationError(
                    "Seul un utilisateur rattache a une direction peut creer une demande."
                )

            user_direction = user.id_direction
            if direction and direction.id_direction != user_direction.id_direction:
                raise serializers.ValidationError(
                    {
                        "id_direction_demandeuse": (
                            "La demande doit etre emise par la direction de l'utilisateur connecte."
                        )
                    }
                )

            if departement and departement.id_departement != user_direction.id_departement_id:
                raise serializers.ValidationError(
                    {
                        "id_departement": (
                            "La demande doit etre envoyee au departement de la direction connectee."
                        )
                    }
                )

            if service and service.id_direction_id != user_direction.id_direction:
                raise serializers.ValidationError(
                    {
                        "id_service_destinataire": (
                            "Le service destinataire doit appartenir a la direction connectee."
                        )
                    }
                )

        if instance is not None and user and not is_admin:
            direction = direction or instance.id_direction_demandeuse
            if (
                user.role_code != ROLE_GESTION
                or user.scope_type != Users.ScopeType.DIRECTION
                or not user.id_direction_id
                or direction.id_direction != user.id_direction_id
            ):
                raise serializers.ValidationError(
                    "Seule la direction demandeuse peut modifier cette demande."
                )

        if direction and departement and direction.id_departement_id != departement.id_departement:
            raise serializers.ValidationError(
                {
                    "id_direction_demandeuse": (
                        "La direction demandeuse doit appartenir au departement choisi."
                    )
                }
            )

        if service and direction and service.id_direction_id != direction.id_direction:
            raise serializers.ValidationError(
                {
                    "id_service_destinataire": (
                        "Le service destinataire doit appartenir a la direction demandeuse."
                    )
                }
            )

        if service and departement and service.id_direction.id_departement_id != departement.id_departement:
            raise serializers.ValidationError(
                {
                    "id_service_destinataire": (
                        "Le service destinataire doit appartenir au departement choisi."
                    )
                }
            )

        if materiel and consommable:
            raise serializers.ValidationError(
                "La demande doit concerner soit un materiel, soit un consommable, pas les deux."
            )

        if type_demande == Demande.TypeDemande.REPARATION:
            if not materiel:
                raise serializers.ValidationError(
                    {"id_materiel": "Une demande de reparation doit indiquer le materiel concerne."}
                )
            if quantite != 1:
                raise serializers.ValidationError(
                    {"quantite_demandee": "Une reparation concerne un seul materiel a la fois."}
                )

        if type_demande == Demande.TypeDemande.REAPPROVISIONNEMENT and not consommable:
            raise serializers.ValidationError(
                {"id_consommable": "Une demande de reapprovisionnement doit indiquer le consommable concerne."}
            )

        return attrs
