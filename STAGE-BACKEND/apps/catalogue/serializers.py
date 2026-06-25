from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.core.serializer_validators import SanitizedModelSerializer, validate_not_blank
from .models import Famille, Categorie, UniteMesure, Fournisseur


class FamilleSerializer(SanitizedModelSerializer):
    class Meta:
        model = Famille
        fields = "__all__"
        extra_kwargs = {
            "code_famille": {
                "validators": [
                    UniqueValidator(
                        queryset=Famille.objects.all(),
                        message="Ce code famille existe déjà.",
                    )
                ]
            }
        }

    def validate_code_famille(self, value):
        return validate_not_blank(value, "Le code de la famille ne peut pas être vide.")

    def validate_nom_famille(self, value):
        return validate_not_blank(value, "Le nom de la famille ne peut pas être vide.")


class CategorieSerializer(SanitizedModelSerializer):
    class Meta:
        model = Categorie
        fields = "__all__"
        extra_kwargs = {
            "code_categorie": {
                "validators": [
                    UniqueValidator(
                        queryset=Categorie.objects.all(),
                        message="Ce code catégorie existe déjà.",
                    )
                ]
            }
        }

    def validate_code_categorie(self, value):
        return validate_not_blank(value, "Le code de la catégorie ne peut pas être vide.")

    def validate_nom_categorie(self, value):
        return validate_not_blank(value, "Le nom de la catégorie ne peut pas être vide.")


class UniteMesureSerializer(SanitizedModelSerializer):
    class Meta:
        model = UniteMesure
        fields = "__all__"
        extra_kwargs = {
            "code_unite": {
                "validators": [
                    UniqueValidator(
                        queryset=UniteMesure.objects.all(),
                        message="Ce code unité existe déjà.",
                    )
                ]
            }
        }

    def validate_code_unite(self, value):
        return validate_not_blank(value, "Le code de l'unité ne peut pas être vide.")

    def validate_nom_unite(self, value):
        return validate_not_blank(value, "Le nom de l'unité ne peut pas être vide.")


class FournisseurSerializer(SanitizedModelSerializer):
    class Meta:
        model = Fournisseur
        fields = "__all__"
        extra_kwargs = {
            "rccm": {
                "validators": [
                    UniqueValidator(
                        queryset=Fournisseur.objects.all(),
                        message="Ce RCCM existe déjà.",
                    )
                ]
            },
            "nif": {
                "validators": [
                    UniqueValidator(
                        queryset=Fournisseur.objects.all(),
                        message="Ce NIF existe déjà.",
                    )
                ]
            },
        }

    def validate_nom_fournisseur(self, value):
        return validate_not_blank(value, "Le nom du fournisseur ne peut pas être vide.")
