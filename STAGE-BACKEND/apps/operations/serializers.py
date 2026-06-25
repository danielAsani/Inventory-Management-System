from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_choice,
    validate_not_future,
    validate_positive,
)
from .models import Affectation, Consommation, MouvementStock

MOUVEMENT_TYPES = {"ENTREE", "SORTIE", "TRANSFERT"}
AFFECTATION_STATUTS = {"ACTIVE", "RETOURNE", "ANNULEE", "TERMINEE"}


class MouvementStockSerializer(SanitizedModelSerializer):
    class Meta:
        model = MouvementStock
        fields = "__all__"

    def validate_type_mouvement(self, value):
        return validate_choice(
            value,
            MOUVEMENT_TYPES,
            "Le type de mouvement doit être ENTREE, SORTIE ou TRANSFERT.",
        )

    def validate_quantite(self, value):
        return validate_positive(value, "La quantité du mouvement doit être supérieure à 0.")

    def validate_date_mouvement(self, value):
        return validate_not_future(value, "La date du mouvement ne peut pas être dans le futur.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        type_mouvement = attrs.get("type_mouvement", getattr(self.instance, "type_mouvement", None))
        source = attrs.get("magasin_source_id", getattr(self.instance, "magasin_source_id", None))
        destination = attrs.get("magasin_destination_id", getattr(self.instance, "magasin_destination_id", None))

        if type_mouvement:
            type_mouvement = type_mouvement.upper()

        if type_mouvement == "TRANSFERT":
            if not source or not destination:
                raise serializers.ValidationError(
                    "Un transfert doit avoir un magasin source et un magasin destination."
                )
            if source == destination:
                raise serializers.ValidationError(
                    "Le magasin source et le magasin destination doivent être différents."
                )
        elif type_mouvement == "SORTIE" and not source:
            raise serializers.ValidationError({"magasin_source_id": "Une sortie doit avoir un magasin source."})
        elif type_mouvement == "ENTREE" and not destination:
            raise serializers.ValidationError(
                {"magasin_destination_id": "Une entrée doit avoir un magasin destination."}
            )

        return attrs


class AffectationSerializer(SanitizedModelSerializer):
    class Meta:
        model = Affectation
        fields = "__all__"

    def validate_date_affectation(self, value):
        return validate_not_future(value, "La date d'affectation ne peut pas être dans le futur.")

    def validate_statut(self, value):
        return validate_choice(
            value,
            AFFECTATION_STATUTS,
            "Le statut de l'affectation doit être ACTIVE, RETOURNE, ANNULEE ou TERMINEE.",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_affectation = attrs.get("date_affectation", getattr(self.instance, "date_affectation", None))
        date_retour = attrs.get("date_retour", getattr(self.instance, "date_retour", None))

        if date_affectation and date_retour and date_retour < date_affectation:
            raise serializers.ValidationError(
                {"date_retour": "La date de retour ne peut pas être avant la date d'affectation."}
            )
        return attrs


class ConsommationSerializer(SanitizedModelSerializer):
    class Meta:
        model = Consommation
        fields = "__all__"

    def validate_quantite(self, value):
        return validate_positive(value, "La quantité consommée doit être supérieure à 0.")

    def validate_date_consommation(self, value):
        return validate_not_future(value, "La date de consommation ne peut pas être dans le futur.")
