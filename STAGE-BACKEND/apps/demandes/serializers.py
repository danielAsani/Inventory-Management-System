from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_choice,
    validate_not_blank,
    validate_not_future,
)
from .models import Demande

DEMANDE_STATUTS = {"BROUILLON", "EN_ATTENTE", "VALIDEE", "REJETEE", "ANNULEE", "TRAITEE"}
DEMANDE_TYPES = {"MATERIEL", "CONSOMMABLE", "SERVICE"}


class DemandeSerializer(SanitizedModelSerializer):
    class Meta:
        model = Demande
        fields = "__all__"

    def validate_code_demande(self, value):
        return validate_not_blank(value, "Le code de la demande ne peut pas être vide.")

    def validate_type_demande(self, value):
        return validate_choice(
            value,
            DEMANDE_TYPES,
            "Le type de demande doit être MATERIEL, CONSOMMABLE ou SERVICE.",
        )

    def validate_statut(self, value):
        return validate_choice(
            value,
            DEMANDE_STATUTS,
            "Le statut de la demande doit être BROUILLON, EN_ATTENTE, VALIDEE, REJETEE, ANNULEE ou TRAITEE.",
        )

    def validate_date_demande(self, value):
        return validate_not_future(value, "La date de demande ne peut pas être dans le futur.")
