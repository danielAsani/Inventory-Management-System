from django.db import transaction
from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_choice,
    validate_not_future,
    validate_not_negative,
)
from .models import Entretien, Reparation
from apps.stock.models import Materiel

ENTRETIEN_TYPES = {"PREVENTIF", "CORRECTIF", "CONTROLE"}
PRESTATAIRE_TYPES = {"AUCUN", "INTERNE", "PRESTATAIRE", "CONSTRUCTEUR"}
ENTRETIEN_STATUTS = {"EN_COURS", "TERMINE", "ANNULE"}
REPARATION_STATUTS = {"EN_ATTENTE", "EN_COURS", "TERMINEE", "ANNULEE"}


class EntretienSerializer(SanitizedModelSerializer):
    materiel_label = serializers.SerializerMethodField()
    materiel_categorie = serializers.CharField(source="id_materiel.id_categorie.nom_categorie", read_only=True)
    materiel_famille = serializers.CharField(source="id_materiel.id_categorie.id_famille.nom_famille", read_only=True)

    class Meta:
        model = Entretien
        fields = "__all__"

    def get_materiel_label(self, obj):
        materiel = obj.id_materiel
        modele = f" {materiel.modele}" if materiel.modele else ""
        return f"{materiel.code_materiel} - {materiel.marque}{modele}"

    def validate_date_entretien(self, value):
        return validate_not_future(value, "La date d'entretien ne peut pas etre dans le futur.")

    def validate_cout_entretien(self, value):
        return validate_not_negative(value, "Le cout d'entretien ne peut pas etre negatif.")

    def validate_kilometrage(self, value):
        return validate_not_negative(value, "Le kilometrage ne peut pas etre negatif.")

    def validate_garantie_entretien_mois(self, value):
        return validate_not_negative(value, "La garantie d'entretien ne peut pas etre negative.")

    def validate_type_entretien(self, value):
        return validate_choice(
            value,
            ENTRETIEN_TYPES,
            "Le type d'entretien doit etre PREVENTIF, CORRECTIF ou CONTROLE.",
        )

    def validate_type_prestataire(self, value):
        return validate_choice(
            value,
            PRESTATAIRE_TYPES,
            "Le type de prestataire doit etre AUCUN, INTERNE, PRESTATAIRE ou CONSTRUCTEUR.",
        )

    def validate_statut(self, value):
        return validate_choice(
            value,
            ENTRETIEN_STATUTS,
            "Le statut doit etre EN_COURS, TERMINE ou ANNULE.",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")
        user_role = getattr(getattr(request, "user", None), "role_code", None)

        if request and request.method == "POST" and user_role == "GESTION":
            allowed_fields = {"id_materiel", "observation"}
            extra_fields = set(self.initial_data.keys()) - allowed_fields
            if extra_fields:
                raise serializers.ValidationError(
                    {field: "Le gestionnaire ne peut renseigner que le materiel et l'observation." for field in extra_fields}
                )

        date_debut = attrs.get("date_entretien", getattr(self.instance, "date_entretien", None))
        date_fin_prevue = attrs.get("date_fin_prevue", getattr(self.instance, "date_fin_prevue", None))
        date_fin_reelle = attrs.get("date_fin_reelle", getattr(self.instance, "date_fin_reelle", None))

        if date_debut and date_fin_prevue and date_fin_prevue < date_debut:
            raise serializers.ValidationError(
                {"date_fin_prevue": "La date de fin prevue ne peut pas etre avant la date d'entretien."}
            )
        if date_debut and date_fin_reelle and date_fin_reelle < date_debut:
            raise serializers.ValidationError(
                {"date_fin_reelle": "La date de fin reelle ne peut pas etre avant la date d'entretien."}
            )
        materiel = attrs.get("id_materiel", getattr(self.instance, "id_materiel", None))
        statut = attrs.get("statut", getattr(self.instance, "statut", None))
        if materiel and statut == "EN_COURS":
            queryset = Entretien.objects.filter(id_materiel=materiel, statut="EN_COURS")
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"id_materiel": "Un entretien en cours existe deja pour ce materiel."}
                )
        return attrs


class ReparationSerializer(SanitizedModelSerializer):
    materiel_label = serializers.SerializerMethodField()
    materiel_categorie = serializers.CharField(source="id_materiel.id_categorie.nom_categorie", read_only=True)
    materiel_famille = serializers.CharField(source="id_materiel.id_categorie.id_famille.nom_famille", read_only=True)

    class Meta:
        model = Reparation
        fields = "__all__"

    def get_materiel_label(self, obj):
        materiel = obj.id_materiel
        modele = f" {materiel.modele}" if materiel.modele else ""
        return f"{materiel.code_materiel} - {materiel.marque}{modele}"

    def validate_date_reparation(self, value):
        return validate_not_future(value, "La date de reparation ne peut pas etre dans le futur.")

    def validate_cout_reparation(self, value):
        return validate_not_negative(value, "Le cout de reparation ne peut pas etre negatif.")

    def validate_garantie_reparation_mois(self, value):
        return validate_not_negative(value, "La garantie de reparation ne peut pas etre negative.")

    def validate_type_prestataire(self, value):
        return validate_choice(
            value,
            PRESTATAIRE_TYPES,
            "Le type de prestataire doit etre AUCUN, INTERNE, PRESTATAIRE ou CONSTRUCTEUR.",
        )

    def validate_statut(self, value):
        return validate_choice(
            value,
            REPARATION_STATUTS,
            "Le statut doit etre EN_ATTENTE, EN_COURS, TERMINEE ou ANNULEE.",
        )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        materiel = attrs.get("id_materiel", getattr(self.instance, "id_materiel", None))
        type_prestataire = attrs.get("type_prestataire", getattr(self.instance, "type_prestataire", None))
        nom_prestataire = attrs.get("nom_prestataire", getattr(self.instance, "nom_prestataire", None))
        date_debut = attrs.get("date_reparation", getattr(self.instance, "date_reparation", None))
        date_fin_prevue = attrs.get("date_fin_prevue", getattr(self.instance, "date_fin_prevue", None))
        date_fin_reelle = attrs.get("date_fin_reelle", getattr(self.instance, "date_fin_reelle", None))

        if type_prestataire == Reparation.TypePrestataire.CONSTRUCTEUR:
            fournisseur = getattr(materiel, "id_fournisseur", None)
            if not fournisseur:
                raise serializers.ValidationError(
                    {"type_prestataire": "Ce materiel n'a pas de fournisseur constructeur associe."}
                )
            attrs["nom_prestataire"] = fournisseur.nom_fournisseur
        elif type_prestataire == Reparation.TypePrestataire.PRESTATAIRE and not nom_prestataire:
            raise serializers.ValidationError(
                {"nom_prestataire": "Le nom du prestataire est obligatoire."}
            )

        if date_debut and date_fin_prevue and date_fin_prevue < date_debut:
            raise serializers.ValidationError(
                {"date_fin_prevue": "La date de fin prevue ne peut pas etre avant la date de reparation."}
            )
        if date_debut and date_fin_reelle and date_fin_reelle < date_debut:
            raise serializers.ValidationError(
                {"date_fin_reelle": "La date de fin reelle ne peut pas etre avant la date de reparation."}
            )
        statut = attrs.get("statut", getattr(self.instance, "statut", None))
        if materiel and statut in {
            Reparation.StatutReparation.EN_ATTENTE,
            Reparation.StatutReparation.EN_COURS,
        }:
            queryset = Reparation.objects.filter(
                id_materiel=materiel,
                statut__in=[
                    Reparation.StatutReparation.EN_ATTENTE,
                    Reparation.StatutReparation.EN_COURS,
                ],
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"id_materiel": "Une reparation ouverte existe deja pour ce materiel."}
                )
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            reparation = super().create(validated_data)
            self._sync_materiel_etat(reparation)
            return reparation

    def update(self, instance, validated_data):
        with transaction.atomic():
            reparation = super().update(instance, validated_data)
            self._sync_materiel_etat(reparation)
            return reparation

    def _sync_materiel_etat(self, reparation):
        materiel = reparation.id_materiel
        if reparation.statut == Reparation.StatutReparation.EN_ATTENTE:
            materiel.etat = Materiel.EtatMateriel.EN_PANNE
            materiel.save(update_fields=["etat"])
            return

        if reparation.statut == Reparation.StatutReparation.EN_COURS:
            materiel.etat = Materiel.EtatMateriel.EN_REPARATION
            materiel.save(update_fields=["etat"])
            return

        has_open_repair = Reparation.objects.filter(
            id_materiel=materiel,
            statut__in=[
                Reparation.StatutReparation.EN_ATTENTE,
                Reparation.StatutReparation.EN_COURS,
            ],
        ).exclude(pk=reparation.pk).exists()
        if not has_open_repair and materiel.etat in {
            Materiel.EtatMateriel.EN_PANNE,
            Materiel.EtatMateriel.EN_REPARATION,
        }:
            materiel.etat = Materiel.EtatMateriel.BON
            materiel.save(update_fields=["etat"])
