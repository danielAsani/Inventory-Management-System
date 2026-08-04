from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    clean_text,
    validate_not_blank,
    validate_unique_optional_text,
    validate_unique_text,
)
from .models import Famille, Categorie, UniteMesure, Fournisseur


class FamilleSerializer(SanitizedModelSerializer):
    class Meta:
        model = Famille
        fields = "__all__"
        read_only_fields = ["code_famille"]

    def validate_nom_famille(self, value):
        value = validate_not_blank(value, "Le nom de la famille ne peut pas etre vide.")
        return validate_unique_text(
            Famille,
            "nom_famille",
            value,
            "Une famille avec ce nom existe deja.",
            self.instance,
        )


class CategorieSerializer(SanitizedModelSerializer):
    famille_nom = serializers.CharField(source="id_famille.nom_famille", read_only=True)

    class Meta:
        model = Categorie
        fields = "__all__"
        read_only_fields = ["code_categorie"]

    def validate_nom_categorie(self, value):
        return validate_not_blank(value, "Le nom de la categorie ne peut pas etre vide.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        nom = attrs.get("nom_categorie", getattr(self.instance, "nom_categorie", None))
        famille = attrs.get("id_famille", getattr(self.instance, "id_famille", None))
        if nom and famille:
            queryset = Categorie.objects.filter(nom_categorie__iexact=nom, id_famille=famille)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"nom_categorie": "Une categorie avec ce nom existe deja dans cette famille."}
                )
        return attrs


class UniteMesureSerializer(SanitizedModelSerializer):
    class Meta:
        model = UniteMesure
        fields = "__all__"
        extra_kwargs = {
            "code_unite": {
                "validators": [
                    UniqueValidator(
                        queryset=UniteMesure.objects.all(),
                        message="Ce code unite existe deja.",
                    )
                ]
            }
        }

    def validate_code_unite(self, value):
        value = validate_not_blank(value, "Le code de l'unite ne peut pas etre vide.").upper()
        return validate_unique_text(
            UniteMesure,
            "code_unite",
            value,
            "Ce code unite existe deja.",
            self.instance,
        )

    def validate_nom_unite(self, value):
        value = validate_not_blank(value, "Le nom de l'unite ne peut pas etre vide.")
        return validate_unique_text(
            UniteMesure,
            "nom_unite",
            value,
            "Une unite avec ce nom existe deja.",
            self.instance,
        )

    def validate_symbole(self, value):
        value = validate_not_blank(value, "Le symbole de l'unite ne peut pas etre vide.").upper()
        return validate_unique_text(
            UniteMesure,
            "symbole",
            value,
            "Une unite avec ce symbole existe deja.",
            self.instance,
        )


class FournisseurSerializer(SanitizedModelSerializer):
    materiels_fournis = serializers.SerializerMethodField()

    class Meta:
        model = Fournisseur
        fields = "__all__"
        extra_kwargs = {
            "rccm": {
                "validators": [
                    UniqueValidator(
                        queryset=Fournisseur.objects.all(),
                        message="Ce RCCM existe deja.",
                    )
                ]
            },
            "nif": {
                "validators": [
                    UniqueValidator(
                        queryset=Fournisseur.objects.all(),
                        message="Ce NIF existe deja.",
                    )
                ]
            },
        }

    def validate_nom_fournisseur(self, value):
        value = validate_not_blank(value, "Le nom du fournisseur ne peut pas etre vide.")
        return validate_unique_text(
            Fournisseur,
            "nom_fournisseur",
            value,
            "Un fournisseur avec ce nom existe deja.",
            self.instance,
        )

    def validate_email(self, value):
        return validate_unique_optional_text(
            Fournisseur,
            "email",
            value,
            "Ce email fournisseur existe deja.",
            self.instance,
        )

    def validate_rccm(self, value):
        if value not in (None, ""):
            value = clean_text(value).upper()
        return validate_unique_optional_text(
            Fournisseur,
            "rccm",
            value,
            "Ce RCCM existe deja.",
            self.instance,
        )

    def validate_nif(self, value):
        if value not in (None, ""):
            value = clean_text(value).upper()
        return validate_unique_optional_text(
            Fournisseur,
            "nif",
            value,
            "Ce NIF existe deja.",
            self.instance,
        )

    def get_materiels_fournis(self, obj):
        return [
            {
                "code": materiel.code_materiel,
                "nom": f"{materiel.marque} {materiel.modele or ''}".strip(),
                "etat": materiel.etat,
            }
            for materiel in obj.materiels.all()[:20]
        ]
