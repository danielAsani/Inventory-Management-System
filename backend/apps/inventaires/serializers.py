from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_choice,
    validate_not_future,
    validate_not_negative,
)
from .models import Inventaire, InventaireDetail

INVENTAIRE_STATUTS = {"EN_COURS", "TERMINE", "ANNULE"}
INVENTAIRE_TYPES = {"GENERAL", "PARTIEL", "PERIODIQUE", "EXCEPTIONNEL"}


class InventaireSerializer(SanitizedModelSerializer):
    class Meta:
        model = Inventaire
        fields = "__all__"

    def validate_date_debut(self, value):
        return validate_not_future(value, "La date de debut d'inventaire ne peut pas etre dans le futur.")

    def validate_type_inventaire(self, value):
        return validate_choice(
            value,
            INVENTAIRE_TYPES,
            "Le type d'inventaire doit etre GENERAL, PARTIEL, PERIODIQUE ou EXCEPTIONNEL.",
        )

    def validate_statut(self, value):
        return validate_choice(
            value,
            INVENTAIRE_STATUTS,
            "Le statut de l'inventaire doit etre EN_COURS, TERMINE ou ANNULE.",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        date_fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))
        statut = attrs.get("statut", getattr(self.instance, "statut", None))

        if date_debut and date_fin and date_fin < date_debut:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin ne peut pas etre avant la date de debut."}
            )
        if statut == "EN_COURS":
            attrs["date_fin"] = None
        return attrs


class InventaireDetailSerializer(SanitizedModelSerializer):
    class Meta:
        model = InventaireDetail
        fields = "__all__"
        read_only_fields = ["ecart"]

    def validate_quantite_theorique(self, value):
        return validate_not_negative(value, "La quantite theorique ne peut pas etre negative.")

    def validate_quantite_reelle(self, value):
        return validate_not_negative(value, "La quantite reelle ne peut pas etre negative.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        materiel = attrs.get("id_materiel", getattr(self.instance, "id_materiel", None))
        consommable = attrs.get("id_consommable", getattr(self.instance, "id_consommable", None))

        if not materiel and not consommable:
            raise serializers.ValidationError(
                "Le detail d'inventaire doit concerner soit un materiel, soit un consommable."
            )
        if materiel and consommable:
            raise serializers.ValidationError(
                "Le detail d'inventaire ne peut pas concerner un materiel et un consommable en meme temps."
            )
        return attrs
