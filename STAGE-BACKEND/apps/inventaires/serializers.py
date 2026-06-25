from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_choice,
    validate_not_future,
    validate_not_negative,
)
from .models import Inventaire, InventaireDetail

INVENTAIRE_STATUTS = {"BROUILLON", "EN_COURS", "TERMINE", "ANNULE"}
INVENTAIRE_TYPES = {"GENERAL", "PARTIEL", "TOURNANT"}


class InventaireSerializer(SanitizedModelSerializer):
    class Meta:
        model = Inventaire
        fields = "__all__"

    def validate_date_debut(self, value):
        return validate_not_future(value, "La date de début d'inventaire ne peut pas être dans le futur.")

    def validate_type_inventaire(self, value):
        return validate_choice(
            value,
            INVENTAIRE_TYPES,
            "Le type d'inventaire doit être GENERAL, PARTIEL ou TOURNANT.",
        )

    def validate_statut(self, value):
        return validate_choice(
            value,
            INVENTAIRE_STATUTS,
            "Le statut de l'inventaire doit être BROUILLON, EN_COURS, TERMINE ou ANNULE.",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))

        if date_debut and date_fin and date_fin < date_debut:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin ne peut pas être avant la date de début."}
            )
        return attrs


class InventaireDetailSerializer(SanitizedModelSerializer):
    class Meta:
        model = InventaireDetail
        fields = "__all__"
        read_only_fields = ["ecart"]

    def validate_quantite_theorique(self, value):
        return validate_not_negative(value, "La quantité théorique ne peut pas être négative.")

    def validate_quantite_reelle(self, value):
        return validate_not_negative(value, "La quantité réelle ne peut pas être négative.")
