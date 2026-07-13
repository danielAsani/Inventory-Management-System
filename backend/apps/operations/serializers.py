from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_choice,
    validate_not_future,
    validate_positive,
)
from apps.stock.models import Materiel
from .models import Affectation, Consommation, MouvementStock

MOUVEMENT_TYPES = {"ENTREE", "SORTIE", "TRANSFERT", "AJUSTEMENT"}
AFFECTATION_STATUTS = {"ACTIVE", "RETOURNEE", "ANNULEE"}


class MouvementStockSerializer(SanitizedModelSerializer):
    class Meta:
        model = MouvementStock
        fields = "__all__"

    def validate_type_mouvement(self, value):
        return validate_choice(
            value,
            MOUVEMENT_TYPES,
            "Le type de mouvement doit etre ENTREE, SORTIE, TRANSFERT ou AJUSTEMENT.",
        )

    def validate_quantite(self, value):
        return validate_positive(value, "La quantite du mouvement doit etre superieure a 0.")

    def validate_date_mouvement(self, value):
        return validate_not_future(value, "La date du mouvement ne peut pas etre dans le futur.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        type_mouvement = attrs.get("type_mouvement", getattr(self.instance, "type_mouvement", None))
        materiel = attrs.get("id_materiel", getattr(self.instance, "id_materiel", None))
        consommable = attrs.get("id_consommable", getattr(self.instance, "id_consommable", None))
        quantite = attrs.get("quantite", getattr(self.instance, "quantite", None))
        source = attrs.get("magasin_source", getattr(self.instance, "magasin_source", None))
        destination = attrs.get("magasin_destination", getattr(self.instance, "magasin_destination", None))

        if type_mouvement:
            type_mouvement = type_mouvement.upper()

        if not materiel and not consommable:
            raise serializers.ValidationError(
                "Le mouvement doit concerner soit un materiel, soit un consommable."
            )
        if materiel and consommable:
            raise serializers.ValidationError(
                "Le mouvement ne peut pas concerner un materiel et un consommable en meme temps."
            )
        if materiel and quantite and quantite != 1:
            raise serializers.ValidationError(
                {"quantite": "Un mouvement de materiel doit avoir une quantite egale a 1."}
            )

        if type_mouvement == "TRANSFERT":
            if not source or not destination:
                raise serializers.ValidationError(
                    "Un transfert doit avoir un magasin source et un magasin destination."
                )
            if source == destination:
                raise serializers.ValidationError(
                    "Le magasin source et le magasin destination doivent etre differents."
                )
        elif type_mouvement == "SORTIE" and not source:
            raise serializers.ValidationError({"magasin_source": "Une sortie doit avoir un magasin source."})
        elif type_mouvement == "ENTREE" and not destination:
            raise serializers.ValidationError(
                {"magasin_destination": "Une entree doit avoir un magasin destination."}
            )

        if materiel:
            self._validate_materiel_movement(materiel, type_mouvement, source)
        if consommable:
            self._validate_consommable_movement(consommable, type_mouvement, quantite, source)

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            mouvement = super().create(validated_data)
            self._apply_movement(mouvement)
            return mouvement

    def update(self, instance, validated_data):
        stock_fields = {
            "id_materiel",
            "id_consommable",
            "type_mouvement",
            "quantite",
            "magasin_source",
            "magasin_destination",
        }
        if stock_fields.intersection(validated_data):
            raise serializers.ValidationError(
                "Un mouvement deja enregistre ne peut pas modifier le stock. Creez un mouvement correctif."
            )
        return super().update(instance, validated_data)

    def _validate_materiel_movement(self, materiel, type_mouvement, source):
        if type_mouvement in {"SORTIE", "TRANSFERT"} and source and materiel.id_magasin_id != source.id_magasin:
            raise serializers.ValidationError(
                {"magasin_source": "Le materiel n'est pas dans le magasin source indique."}
            )
        if type_mouvement in {"SORTIE", "TRANSFERT"} and materiel.etat == Materiel.EtatMateriel.AFFECTE:
            raise serializers.ValidationError(
                {"id_materiel": "Le materiel est deja affecte et ne peut pas sortir du stock."}
            )

    def _validate_consommable_movement(self, consommable, type_mouvement, quantite, source):
        if type_mouvement in {"SORTIE", "TRANSFERT"} and source and consommable.id_magasin_id != source.id_magasin:
            raise serializers.ValidationError(
                {"magasin_source": "Le consommable n'est pas dans le magasin source indique."}
            )
        if type_mouvement == "SORTIE" and quantite and consommable.quantite_stock < Decimal(quantite):
            raise serializers.ValidationError(
                {"quantite": "Stock insuffisant pour cette sortie."}
            )

    def _apply_movement(self, mouvement):
        if mouvement.id_materiel_id:
            self._apply_materiel_movement(mouvement)
        if mouvement.id_consommable_id:
            self._apply_consommable_movement(mouvement)

    def _apply_materiel_movement(self, mouvement):
        materiel = mouvement.id_materiel
        if mouvement.type_mouvement in {"ENTREE", "TRANSFERT"}:
            materiel.id_magasin = mouvement.magasin_destination
            if materiel.etat in {Materiel.EtatMateriel.NEUF, Materiel.EtatMateriel.HORS_SERVICE}:
                materiel.etat = Materiel.EtatMateriel.EN_STOCK
            materiel.save(update_fields=["id_magasin", "etat"])
        elif mouvement.type_mouvement == "SORTIE":
            materiel.id_magasin = None
            materiel.save(update_fields=["id_magasin"])

    def _apply_consommable_movement(self, mouvement):
        consommable = mouvement.id_consommable
        quantite = Decimal(mouvement.quantite)
        if mouvement.type_mouvement == "ENTREE":
            consommable.quantite_stock += quantite
            consommable.id_magasin = mouvement.magasin_destination
            consommable.save(update_fields=["quantite_stock", "id_magasin"])
        elif mouvement.type_mouvement == "SORTIE":
            consommable.quantite_stock -= quantite
            consommable.save(update_fields=["quantite_stock"])
        elif mouvement.type_mouvement == "TRANSFERT":
            consommable.id_magasin = mouvement.magasin_destination
            consommable.save(update_fields=["id_magasin"])


class AffectationSerializer(SanitizedModelSerializer):
    class Meta:
        model = Affectation
        fields = "__all__"

    def validate_date_affectation(self, value):
        return validate_not_future(value, "La date d'affectation ne peut pas etre dans le futur.")

    def validate_statut(self, value):
        return validate_choice(
            value,
            AFFECTATION_STATUTS,
            "Le statut de l'affectation doit etre ACTIVE, RETOURNEE ou ANNULEE.",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        materiel = attrs.get("id_materiel", getattr(self.instance, "id_materiel", None))
        statut = attrs.get("statut", getattr(self.instance, "statut", None))
        date_affectation = attrs.get("date_affectation", getattr(self.instance, "date_affectation", None))
        date_retour = attrs.get("date_retour", getattr(self.instance, "date_retour", None))

        if date_affectation and date_retour and date_retour < date_affectation:
            raise serializers.ValidationError(
                {"date_retour": "La date de retour ne peut pas etre avant la date d'affectation."}
            )
        if materiel and statut == "ACTIVE":
            active_query = Affectation.objects.filter(id_materiel=materiel, statut="ACTIVE")
            if self.instance:
                active_query = active_query.exclude(pk=self.instance.pk)
            if active_query.exists():
                raise serializers.ValidationError(
                    {"id_materiel": "Ce materiel a deja une affectation active."}
                )
            if materiel.etat == Materiel.EtatMateriel.HORS_SERVICE:
                raise serializers.ValidationError(
                    {"id_materiel": "Un materiel hors service ne peut pas etre affecte."}
                )
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            affectation = super().create(validated_data)
            self._sync_materiel_state(affectation)
            return affectation

    def update(self, instance, validated_data):
        with transaction.atomic():
            affectation = super().update(instance, validated_data)
            self._sync_materiel_state(affectation)
            return affectation

    def _sync_materiel_state(self, affectation):
        materiel = affectation.id_materiel
        if affectation.statut == "ACTIVE":
            materiel.etat = Materiel.EtatMateriel.AFFECTE
            materiel.save(update_fields=["etat"])
        elif not Affectation.objects.filter(id_materiel=materiel, statut="ACTIVE").exclude(pk=affectation.pk).exists():
            if materiel.etat == Materiel.EtatMateriel.AFFECTE:
                materiel.etat = Materiel.EtatMateriel.EN_STOCK
                materiel.save(update_fields=["etat"])


class ConsommationSerializer(SanitizedModelSerializer):
    class Meta:
        model = Consommation
        fields = "__all__"

    def validate_quantite(self, value):
        return validate_positive(value, "La quantite consommee doit etre superieure a 0.")

    def validate_date_consommation(self, value):
        return validate_not_future(value, "La date de consommation ne peut pas etre dans le futur.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        consommable = attrs.get("id_consommable", getattr(self.instance, "id_consommable", None))
        quantite = attrs.get("quantite", getattr(self.instance, "quantite", None))
        if self.instance and ("id_consommable" in attrs or "quantite" in attrs):
            raise serializers.ValidationError(
                "Une consommation deja enregistree ne peut pas modifier le stock. Creez une correction."
            )
        if consommable and quantite and consommable.quantite_stock < Decimal(quantite):
            raise serializers.ValidationError({"quantite": "Stock insuffisant pour cette consommation."})
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            consommation = super().create(validated_data)
            consommable = consommation.id_consommable
            consommable.quantite_stock -= Decimal(consommation.quantite)
            consommable.save(update_fields=["quantite_stock"])
            return consommation
