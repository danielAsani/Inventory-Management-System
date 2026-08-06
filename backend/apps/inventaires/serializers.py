from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_choice,
    validate_not_future,
    validate_not_negative,
)
from apps.organisation.models import Departement, Direction
from .models import Inventaire, InventaireDetail

INVENTAIRE_STATUTS = {"EN_COURS", "TERMINE", "ANNULE"}
INVENTAIRE_TYPES = {"GENERAL", "PARTIEL", "PERIODIQUE", "EXCEPTIONNEL"}


class InventaireSerializer(SanitizedModelSerializer):
    effectue_par_nom = serializers.CharField(source="effectue_par.nom_users", read_only=True)
    cree_par_nom = serializers.CharField(source="cree_par.nom_users", read_only=True)
    entite_nom = serializers.SerializerMethodField()
    nombre_lignes = serializers.SerializerMethodField()
    nombre_ecarts = serializers.SerializerMethodField()
    ecart_total = serializers.SerializerMethodField()
    lignes_comptage = serializers.SerializerMethodField()

    class Meta:
        model = Inventaire
        fields = "__all__"
        read_only_fields = ["code_inventaire", "cree_par"]

    def get_entite_nom(self, obj):
        model_by_type = {
            "DEPARTEMENT": (Departement, "id_departement", "nom_departement"),
            "DIRECTION": (Direction, "id_direction", "nom_direction"),
        }
        model_info = model_by_type.get(obj.entite_type)
        if not model_info or not obj.entite_id:
            return "-"

        model, pk_field, name_field = model_info
        entite = model.objects.filter(**{pk_field: obj.entite_id}).first()
        return getattr(entite, name_field, "-") if entite else "-"

    def get_nombre_lignes(self, obj):
        return obj.details.count()

    def get_nombre_ecarts(self, obj):
        return obj.details.exclude(ecart=0).count()

    def get_ecart_total(self, obj):
        return sum(detail.ecart for detail in obj.details.all())

    def get_lignes_comptage(self, obj):
        return [
            {
                "article": self._detail_article_label(detail),
                "theorique": detail.quantite_theorique,
                "reel": detail.quantite_reelle,
                "ecart": detail.ecart,
            }
            for detail in obj.details.all()[:30]
        ]

    def _detail_article_label(self, detail):
        if detail.id_materiel:
            materiel = detail.id_materiel
            modele = f" {materiel.modele}" if materiel.modele else ""
            return f"{materiel.code_materiel} - {materiel.marque}{modele}"
        if detail.id_consommable:
            return f"{detail.id_consommable.code_consommable} - {detail.id_consommable.nom_consommable}"
        return "-"

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
            entite_type = attrs.get("entite_type", getattr(self.instance, "entite_type", None))
            entite_id = attrs.get("entite_id", getattr(self.instance, "entite_id", None))
            if entite_type and entite_id:
                queryset = Inventaire.objects.filter(
                    entite_type=entite_type,
                    entite_id=entite_id,
                    statut="EN_COURS",
                )
                if self.instance:
                    queryset = queryset.exclude(pk=self.instance.pk)
                if queryset.exists():
                    raise serializers.ValidationError(
                        {"entite_id": "Un inventaire en cours existe deja pour ce perimetre."}
                    )
        return attrs


class InventaireDetailSerializer(SanitizedModelSerializer):
    inventaire_code = serializers.CharField(source="id_inventaire.code_inventaire", read_only=True)
    inventaire_perimetre = serializers.CharField(source="id_inventaire.entite_type", read_only=True)
    materiel_label = serializers.SerializerMethodField()
    consommable_label = serializers.SerializerMethodField()
    article_type = serializers.SerializerMethodField()
    article_label = serializers.SerializerMethodField()
    categorie_nom = serializers.SerializerMethodField()
    famille_nom = serializers.SerializerMethodField()

    class Meta:
        model = InventaireDetail
        fields = "__all__"
        read_only_fields = ["ecart"]

    def get_materiel_label(self, obj):
        if not obj.id_materiel:
            return "-"
        materiel = obj.id_materiel
        modele = f" {materiel.modele}" if materiel.modele else ""
        return f"{materiel.code_materiel} - {materiel.marque}{modele}"

    def get_consommable_label(self, obj):
        if not obj.id_consommable:
            return "-"
        return f"{obj.id_consommable.code_consommable} - {obj.id_consommable.nom_consommable}"

    def get_article_type(self, obj):
        if obj.id_materiel_id:
            return "Materiel"
        if obj.id_consommable_id:
            return "Consommable"
        return "-"

    def get_article_label(self, obj):
        if obj.id_materiel_id:
            return self.get_materiel_label(obj)
        if obj.id_consommable_id:
            return self.get_consommable_label(obj)
        return "-"

    def get_categorie_nom(self, obj):
        article = obj.id_materiel or obj.id_consommable
        if not article or not article.id_categorie_id:
            return "-"
        return article.id_categorie.nom_categorie

    def get_famille_nom(self, obj):
        article = obj.id_materiel or obj.id_consommable
        if not article or not article.id_categorie_id or not article.id_categorie.id_famille_id:
            return "-"
        return article.id_categorie.id_famille.nom_famille

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
        inventaire = attrs.get("id_inventaire", getattr(self.instance, "id_inventaire", None))
        if inventaire and materiel:
            queryset = InventaireDetail.objects.filter(id_inventaire=inventaire, id_materiel=materiel)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"id_materiel": "Ce materiel est deja compte dans cet inventaire."}
                )
        if inventaire and consommable:
            queryset = InventaireDetail.objects.filter(id_inventaire=inventaire, id_consommable=consommable)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"id_consommable": "Ce consommable est deja compte dans cet inventaire."}
                )
        return attrs
