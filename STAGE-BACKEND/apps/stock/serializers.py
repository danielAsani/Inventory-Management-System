from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_not_blank,
    validate_not_future,
    validate_not_negative,
)
from .models import Magasin, Materiel, Consommable


class MagasinSerializer(SanitizedModelSerializer):
    class Meta:
        model = Magasin
        fields = "__all__"
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

    def validate_code_magasin(self, value):
        return validate_not_blank(value, "Le code du magasin ne peut pas être vide.")

    def validate_nom_magasin(self, value):
        return validate_not_blank(value, "Le nom du magasin ne peut pas être vide.")


class MaterielSerializer(SanitizedModelSerializer):
    class Meta:
        model = Materiel
        fields = "__all__"
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
        return attrs


class ConsommableSerializer(SanitizedModelSerializer):
    class Meta:
        model = Consommable
        fields = "__all__"
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
