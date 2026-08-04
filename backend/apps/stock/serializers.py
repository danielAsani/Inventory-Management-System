from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_not_blank,
    validate_not_future,
    validate_not_negative,
    validate_unique_optional_text,
    validate_unique_text,
)
from .models import Magasin, Materiel, Consommable


class MagasinSerializer(SanitizedModelSerializer):
    direction_nom = serializers.SerializerMethodField()
    departement_nom = serializers.SerializerMethodField()

    class Meta:
        model = Magasin
        fields = [
            "id_magasin",
            "code_magasin",
            "nom_magasin",
            "id_direction",
            "direction_nom",
            "departement_nom",
            "description_localisation",
            "date_creation",
            "statut",
        ]
        extra_kwargs = {
            "code_magasin": {
                "validators": [
                    UniqueValidator(
                        queryset=Magasin.objects.all(),
                        message="Ce code magasin existe déjà.",
                    )
                ]
            }
        }

    def get_direction(self, obj):
        return obj.id_direction or getattr(obj.id_service, "id_direction", None)

    def get_direction_nom(self, obj):
        direction = self.get_direction(obj)
        return direction.nom_direction if direction else "-"

    def get_departement_nom(self, obj):
        direction = self.get_direction(obj)
        if not direction or not direction.id_departement_id:
            return "-"
        return direction.id_departement.nom_departement

    def validate_code_magasin(self, value):
        return validate_not_blank(value, "Le code du magasin ne peut pas être vide.")

    def validate_nom_magasin(self, value):
        value = validate_not_blank(value, "Le nom du magasin ne peut pas être vide.")
        return validate_unique_text(
            Magasin,
            "nom_magasin",
            value,
            "Un magasin avec ce nom existe deja.",
            self.instance,
        )


class MaterielSerializer(SanitizedModelSerializer):
    categorie_nom = serializers.CharField(source="id_categorie.nom_categorie", read_only=True)
    famille_nom = serializers.CharField(source="id_categorie.id_famille.nom_famille", read_only=True)
    magasin_nom = serializers.CharField(source="id_magasin.nom_magasin", read_only=True)
    fournisseur_nom = serializers.CharField(source="id_fournisseur.nom_fournisseur", read_only=True)
    quantite_creation = serializers.IntegerField(
        write_only=True,
        required=False,
        default=1,
        min_value=1,
        max_value=100,
        error_messages={
            "min_value": "La quantite doit etre au moins egale a 1.",
            "max_value": "La quantite ne peut pas depasser 100 materiels par creation.",
        },
    )

    class Meta:
        model = Materiel
        fields = "__all__"
        read_only_fields = ["code_materiel", "numero_serie", "code_barre", "qr_code", "statut_stock"]
        extra_kwargs = {
            "code_materiel": {
                "validators": [
                    UniqueValidator(
                        queryset=Materiel.objects.all(),
                        message="Ce code matériel existe déjà.",
                    )
                ]
            },
            "numero_serie": {
                "validators": [
                    UniqueValidator(
                        queryset=Materiel.objects.all(),
                        message="Ce numéro de série existe déjà.",
                    )
                ]
            },
            "code_barre": {
                "validators": [
                    UniqueValidator(
                        queryset=Materiel.objects.all(),
                        message="Ce code-barres existe déjà.",
                    )
                ]
            },
            "qr_code": {
                "validators": [
                    UniqueValidator(
                        queryset=Materiel.objects.all(),
                        message="Ce QR code existe déjà.",
                    )
                ]
            },
        }

    def validate_code_materiel(self, value):
        return validate_not_blank(value, "Le code du matériel ne peut pas être vide.")

    def validate_marque(self, value):
        if value is not None:
            return validate_not_blank(value, "La marque ne peut pas contenir uniquement des espaces.")
        return value

    def validate_modele(self, value):
        if value is not None:
            return validate_not_blank(value, "Le modèle ne peut pas contenir uniquement des espaces.")
        return value

    def validate_numero_serie(self, value):
        return validate_unique_optional_text(
            Materiel,
            "numero_serie",
            value,
            "Ce numero de serie existe deja.",
            self.instance,
        )

    def validate_prix_achat(self, value):
        return validate_not_negative(value, "Le prix d'achat ne peut pas être négatif.")

    def validate_duree_garantie_mois(self, value):
        return validate_not_negative(value, "La durée de garantie ne peut pas être négative.")

    def validate_date_achat(self, value):
        return validate_not_future(value, "La date d'achat ne peut pas être dans le futur.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        date_achat = attrs.get("date_achat", getattr(self.instance, "date_achat", None))
        garantie_fin = attrs.get("garantie_fin", getattr(self.instance, "garantie_fin", None))

        if date_achat and garantie_fin and garantie_fin < date_achat:
            raise serializers.ValidationError(
                {"garantie_fin": "La fin de garantie ne peut pas être avant la date d'achat."}
            )
        categorie = attrs.get("id_categorie", getattr(self.instance, "id_categorie", None))
        marque = attrs.get("marque", getattr(self.instance, "marque", None))
        modele = attrs.get("modele", getattr(self.instance, "modele", None))
        numero_serie = attrs.get("numero_serie", getattr(self.instance, "numero_serie", None))
        if not numero_serie and categorie and marque and modele:
            queryset = Materiel.objects.filter(
                id_categorie=categorie,
                marque__iexact=marque,
                modele__iexact=modele,
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"modele": "Un materiel sans numero de serie avec cette categorie, marque et modele existe deja."}
                )
        return attrs

    def create(self, validated_data):
        quantity = validated_data.pop("quantite_creation", 1)
        total_price = validated_data.get("prix_achat")
        if total_price is not None and quantity > 1:
            validated_data["prix_achat"] = (total_price / Decimal(quantity)).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )

        validated_data["statut_stock"] = (
            Materiel.StatutStock.EN_STOCK if validated_data.get("id_magasin") else Materiel.StatutStock.HORS_STOCK
        )

        first_material = None
        with transaction.atomic():
            for _ in range(quantity):
                material = Materiel.objects.create(**validated_data)
                if first_material is None:
                    first_material = material
        return first_material


class ConsommableSerializer(SanitizedModelSerializer):
    categorie_nom = serializers.CharField(source="id_categorie.nom_categorie", read_only=True)
    famille_nom = serializers.CharField(source="id_categorie.id_famille.nom_famille", read_only=True)
    unite_nom = serializers.CharField(source="id_unite.nom_unite", read_only=True)
    magasin_nom = serializers.CharField(source="id_magasin.nom_magasin", read_only=True)

    class Meta:
        model = Consommable
        fields = "__all__"
        read_only_fields = ["code_consommable"]
        extra_kwargs = {
            "code_consommable": {
                "validators": [
                    UniqueValidator(
                        queryset=Consommable.objects.all(),
                        message="Ce code consommable existe déjà.",
                    )
                ]
            }
        }

    def validate_code_consommable(self, value):
        return validate_not_blank(value, "Le code du consommable ne peut pas être vide.")

    def validate_nom_consommable(self, value):
        return validate_not_blank(value, "Le nom du consommable ne peut pas être vide.")

    def validate_quantite_stock(self, value):
        return validate_not_negative(value, "La quantité en stock ne peut pas être négative.")

    def validate_seuil_alerte(self, value):
        return validate_not_negative(value, "Le seuil d'alerte ne peut pas être négatif.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        nom = attrs.get("nom_consommable", getattr(self.instance, "nom_consommable", None))
        categorie = attrs.get("id_categorie", getattr(self.instance, "id_categorie", None))
        unite = attrs.get("id_unite", getattr(self.instance, "id_unite", None))
        if nom and categorie and unite:
            queryset = Consommable.objects.filter(
                nom_consommable__iexact=nom,
                id_categorie=categorie,
                id_unite=unite,
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"nom_consommable": "Un consommable avec ce nom existe deja pour cette categorie et cette unite."}
                )
        return attrs
