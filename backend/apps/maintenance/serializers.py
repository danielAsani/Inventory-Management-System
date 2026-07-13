from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_choice,
    validate_not_future,
    validate_not_negative,
)
from .models import Entretien, Reparation

ENTRETIEN_TYPES = {"PREVENTIF", "CORRECTIF", "CONTROLE"}
PRESTATAIRE_TYPES = {"AUCUN", "INTERNE", "PRESTATAIRE", "CONSTRUCTEUR"}
ENTRETIEN_STATUTS = {"PLANIFIE", "EN_COURS", "TERMINE", "ANNULE"}
REPARATION_STATUTS = {"EN_ATTENTE", "EN_COURS", "TERMINEE", "ANNULEE"}


class EntretienSerializer(SanitizedModelSerializer):
    class Meta:
        model = Entretien
        fields = "__all__"

    def validate_date_entretien(self, value):
        return validate_not_future(value, "La date d'entretien ne peut pas être dans le futur.")

    def validate_cout_entretien(self, value):
        return validate_not_negative(value, "Le coût d'entretien ne peut pas être négatif.")

    def validate_kilometrage(self, value):
        return validate_not_negative(value, "Le kilométrage ne peut pas être négatif.")

    def validate_garantie_entretien_mois(self, value):
        return validate_not_negative(value, "La garantie d'entretien ne peut pas être négative.")

    def validate_type_entretien(self, value):
        return validate_choice(
            value,
            ENTRETIEN_TYPES,
            "Le type d'entretien doit être PREVENTIF ou CORRECTIF.",
        )

    def validate_type_prestataire(self, value):
        return validate_choice(
            value,
            PRESTATAIRE_TYPES,
            "Le type de prestataire doit être INTERNE ou EXTERNE.",
        )

    def validate_statut(self, value):
        return validate_choice(
            value,
            ENTRETIEN_STATUTS,
            "Le statut doit être PLANIFIE, EN_COURS, TERMINE ou ANNULE.",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_debut = attrs.get("date_entretien", getattr(self.instance, "date_entretien", None))
        date_fin_prevue = attrs.get("date_fin_prevue", getattr(self.instance, "date_fin_prevue", None))
        date_fin_reelle = attrs.get("date_fin_reelle", getattr(self.instance, "date_fin_reelle", None))

        if date_debut and date_fin_prevue and date_fin_prevue < date_debut:
            raise serializers.ValidationError(
                {"date_fin_prevue": "La date de fin prévue ne peut pas être avant la date d'entretien."}
            )
        if date_debut and date_fin_reelle and date_fin_reelle < date_debut:
            raise serializers.ValidationError(
                {"date_fin_reelle": "La date de fin réelle ne peut pas être avant la date d'entretien."}
            )
        return attrs


class ReparationSerializer(SanitizedModelSerializer):
    class Meta:
        model = Reparation
        fields = "__all__"

    def validate_date_reparation(self, value):
        return validate_not_future(value, "La date de réparation ne peut pas être dans le futur.")

    def validate_cout_reparation(self, value):
        return validate_not_negative(value, "Le coût de réparation ne peut pas être négatif.")

    def validate_garantie_reparation_mois(self, value):
        return validate_not_negative(value, "La garantie de réparation ne peut pas être négative.")

    def validate_type_prestataire(self, value):
        return validate_choice(
            value,
            PRESTATAIRE_TYPES,
            "Le type de prestataire doit être INTERNE ou EXTERNE.",
        )

    def validate_statut(self, value):
        return validate_choice(
            value,
            REPARATION_STATUTS,
            "Le statut doit être PLANIFIE, EN_COURS, TERMINE ou ANNULE.",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_debut = attrs.get("date_reparation", getattr(self.instance, "date_reparation", None))
        date_fin_prevue = attrs.get("date_fin_prevue", getattr(self.instance, "date_fin_prevue", None))
        date_fin_reelle = attrs.get("date_fin_reelle", getattr(self.instance, "date_fin_reelle", None))

        if date_debut and date_fin_prevue and date_fin_prevue < date_debut:
            raise serializers.ValidationError(
                {"date_fin_prevue": "La date de fin prévue ne peut pas être avant la date de réparation."}
            )
        if date_debut and date_fin_reelle and date_fin_reelle < date_debut:
            raise serializers.ValidationError(
                {"date_fin_reelle": "La date de fin réelle ne peut pas être avant la date de réparation."}
            )
        return attrs
