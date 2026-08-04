from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    clean_text,
    validate_choice,
    validate_not_blank,
    validate_not_future,
    validate_positive,
)
from apps.comptes.models import Users
from apps.organisation.models import Departement, Direction
from apps.stock.models import Magasin, Materiel
from .models import Affectation, Consommation, MouvementStock

MOUVEMENT_TYPES = {"ENTREE", "SORTIE", "TRANSFERT", "AJUSTEMENT"}
AFFECTATION_STATUTS = {"ACTIVE", "RETOURNEE", "ANNULEE"}


class MouvementStockSerializer(SanitizedModelSerializer):
    article = serializers.SerializerMethodField()
    article_type = serializers.SerializerMethodField()
    magasin_source_nom = serializers.SerializerMethodField()
    magasin_destination_nom = serializers.SerializerMethodField()
    fait_par_nom = serializers.CharField(source="fait_par.nom_users", read_only=True)

    class Meta:
        model = MouvementStock
        fields = "__all__"

    def get_article(self, obj):
        if obj.id_materiel:
            modele = f" {obj.id_materiel.modele}" if obj.id_materiel.modele else ""
            return f"{obj.id_materiel.code_materiel} - {obj.id_materiel.marque}{modele}"
        if obj.id_consommable:
            return f"{obj.id_consommable.code_consommable} - {obj.id_consommable.nom_consommable}"
        return "-"

    def get_article_type(self, obj):
        if obj.id_materiel_id:
            return "Materiel"
        if obj.id_consommable_id:
            return "Consommable"
        return "-"

    def get_magasin_source_nom(self, obj):
        if not obj.magasin_source:
            return "-"
        return obj.magasin_source.nom_magasin

    def get_magasin_destination_nom(self, obj):
        if not obj.magasin_destination:
            return "-"
        return obj.magasin_destination.nom_magasin

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
        if type_mouvement in {"SORTIE", "TRANSFERT"} and materiel.statut_stock == Materiel.StatutStock.AFFECTE:
            raise serializers.ValidationError(
                {"id_materiel": "Le materiel est deja affecte et ne peut pas sortir du stock."}
            )

    def _validate_consommable_movement(self, consommable, type_mouvement, quantite, source):
        if type_mouvement in {"SORTIE", "TRANSFERT"} and source and consommable.id_magasin_id != source.id_magasin:
            raise serializers.ValidationError(
                {"magasin_source": "Le consommable n'est pas dans le magasin source indique."}
            )
        if type_mouvement in {"SORTIE", "TRANSFERT"} and quantite and consommable.quantite_stock < Decimal(quantite):
            raise serializers.ValidationError(
                {"quantite": "Stock insuffisant pour ce mouvement."}
            )
        if (
            type_mouvement == "TRANSFERT"
            and quantite
            and consommable.quantite_stock != Decimal(quantite)
        ):
            raise serializers.ValidationError(
                {"quantite": "Le transfert partiel d'un consommable n'est pas encore supporte. Transferez toute la quantite de cette ligne."}
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
            materiel.statut_stock = Materiel.StatutStock.EN_STOCK
            materiel.save(update_fields=["id_magasin", "statut_stock"])
        elif mouvement.type_mouvement == "SORTIE":
            materiel.id_magasin = None
            materiel.statut_stock = Materiel.StatutStock.HORS_STOCK
            materiel.save(update_fields=["id_magasin", "statut_stock"])

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
        elif mouvement.type_mouvement == "AJUSTEMENT":
            consommable.quantite_stock = quantite
            consommable.save(update_fields=["quantite_stock"])


class AffectationSerializer(SanitizedModelSerializer):
    materiel_label = serializers.SerializerMethodField()
    entite_nom = serializers.SerializerMethodField()
    agent_departement_nom = serializers.CharField(source="agent_id_departement.nom_departement", read_only=True)
    agent_direction_nom = serializers.CharField(source="agent_id_direction.nom_direction", read_only=True)

    class Meta:
        model = Affectation
        fields = "__all__"
        read_only_fields = ["code_affectation", "code_barre", "qr_code"]

    def get_materiel_label(self, obj):
        materiel = obj.id_materiel
        modele = f" {materiel.modele}" if materiel.modele else ""
        return f"{materiel.code_materiel} - {materiel.marque}{modele}"

    def get_entite_nom(self, obj):
        if obj.entite_type == Affectation.EntiteType.AGENT:
            matricule = f"{obj.agent_matricule} - " if obj.agent_matricule else ""
            return f"{matricule}{obj.agent_nom_complet or '-'}"

        model_by_type = {
            "DEPARTEMENT": (Departement, "id_departement", "nom_departement"),
            "DIRECTION": (Direction, "id_direction", "nom_direction"),
            "UTILISATEUR": (Users, "id_users", "nom_users"),
            "MAGASIN": (Magasin, "id_magasin", "nom_magasin"),
        }
        model_info = model_by_type.get(obj.entite_type)
        if not model_info or not obj.entite_id:
            return "-"

        model, pk_field, name_field = model_info
        entite = model.objects.filter(**{pk_field: obj.entite_id}).first()
        return getattr(entite, name_field, "-") if entite else "-"

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
        entite_type = attrs.get("entite_type", getattr(self.instance, "entite_type", None))
        entite_id = attrs.get("entite_id", getattr(self.instance, "entite_id", None))
        statut = attrs.get("statut", getattr(self.instance, "statut", None))
        date_affectation = attrs.get("date_affectation", getattr(self.instance, "date_affectation", None))
        date_retour = attrs.get("date_retour", getattr(self.instance, "date_retour", None))
        agent_departement = attrs.get("agent_id_departement", getattr(self.instance, "agent_id_departement", None))
        agent_direction = attrs.get("agent_id_direction", getattr(self.instance, "agent_id_direction", None))

        if attrs.get("agent_matricule"):
            attrs["agent_matricule"] = clean_text(attrs["agent_matricule"]).upper()
        if attrs.get("agent_nom_complet"):
            attrs["agent_nom_complet"] = clean_text(attrs["agent_nom_complet"])
        if attrs.get("agent_telephone"):
            attrs["agent_telephone"] = clean_text(attrs["agent_telephone"])

        if date_affectation and date_retour and date_retour < date_affectation:
            raise serializers.ValidationError(
                {"date_retour": "La date de retour ne peut pas etre avant la date d'affectation."}
            )

        if entite_type == Affectation.EntiteType.AGENT:
            matricule = validate_not_blank(
                attrs.get("agent_matricule", getattr(self.instance, "agent_matricule", None)),
                "Le matricule de l'agent est obligatoire.",
            )
            nom_complet = validate_not_blank(
                attrs.get("agent_nom_complet", getattr(self.instance, "agent_nom_complet", None)),
                "Le nom complet de l'agent est obligatoire.",
            )
            attrs["agent_matricule"] = matricule.upper()
            attrs["agent_nom_complet"] = nom_complet
            attrs["entite_id"] = None

            if not agent_departement:
                raise serializers.ValidationError(
                    {"agent_id_departement": "Le departement de l'agent est obligatoire."}
                )
            if not agent_direction:
                raise serializers.ValidationError(
                    {"agent_id_direction": "La direction de l'agent est obligatoire."}
                )
            if agent_direction.id_departement_id != agent_departement.id_departement:
                raise serializers.ValidationError(
                    {"agent_id_direction": "La direction doit appartenir au departement choisi."}
                )
            attrs["agent_id_service"] = None
        else:
            if not entite_id:
                raise serializers.ValidationError({"entite_id": "Le destinataire est obligatoire."})
            attrs["agent_id_departement"] = None
            attrs["agent_id_direction"] = None
            attrs["agent_id_service"] = None
            attrs["agent_matricule"] = None
            attrs["agent_nom_complet"] = None
            attrs["agent_telephone"] = None

        if materiel and statut == "ACTIVE":
            active_query = Affectation.objects.filter(id_materiel=materiel, statut="ACTIVE")
            if self.instance:
                active_query = active_query.exclude(pk=self.instance.pk)
            if active_query.exists():
                raise serializers.ValidationError(
                    {"id_materiel": "Ce materiel a deja une affectation active."}
                )
            if materiel.statut_stock != Materiel.StatutStock.EN_STOCK:
                raise serializers.ValidationError(
                    {"id_materiel": "Seul un materiel disponible en stock peut etre affecte."}
                )
            if materiel.etat in {
                Materiel.EtatMateriel.HORS_SERVICE,
                Materiel.EtatMateriel.EN_PANNE,
                Materiel.EtatMateriel.EN_REPARATION,
            }:
                raise serializers.ValidationError(
                    {"id_materiel": "Un materiel en panne, en reparation ou hors service ne peut pas etre affecte."}
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
            materiel.statut_stock = Materiel.StatutStock.AFFECTE
            materiel.save(update_fields=["statut_stock"])
        elif not Affectation.objects.filter(id_materiel=materiel, statut="ACTIVE").exclude(pk=affectation.pk).exists():
            if materiel.statut_stock == Materiel.StatutStock.AFFECTE:
                materiel.statut_stock = Materiel.StatutStock.EN_STOCK if materiel.id_magasin_id else Materiel.StatutStock.HORS_STOCK
                materiel.save(update_fields=["statut_stock"])


class ConsommationSerializer(SanitizedModelSerializer):
    consommable_label = serializers.SerializerMethodField()
    departement_nom = serializers.CharField(source="id_departement.nom_departement", read_only=True)
    direction_nom = serializers.CharField(source="id_direction.nom_direction", read_only=True)
    destination_nom = serializers.SerializerMethodField()
    fait_par_nom = serializers.CharField(source="fait_par.nom_users", read_only=True)

    class Meta:
        model = Consommation
        fields = "__all__"

    def get_consommable_label(self, obj):
        consommable = obj.id_consommable
        categorie = consommable.id_categorie.nom_categorie if consommable.id_categorie_id else "-"
        famille = (
            consommable.id_categorie.id_famille.nom_famille
            if consommable.id_categorie_id and consommable.id_categorie.id_famille_id
            else "-"
        )
        return f"{consommable.code_consommable} - {consommable.nom_consommable} ({categorie} / {famille})"

    def get_destination_nom(self, obj):
        if obj.destination_type == Consommation.DestinationType.DIRECTION and obj.id_direction_id:
            return obj.id_direction.nom_direction
        if obj.destination_type == Consommation.DestinationType.DEPARTEMENT and obj.id_departement_id:
            return obj.id_departement.nom_departement
        return "-"

    def validate_quantite(self, value):
        return validate_positive(value, "La quantite consommee doit etre superieure a 0.")

    def validate_date_consommation(self, value):
        return validate_not_future(value, "La date de consommation ne peut pas etre dans le futur.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        consommable = attrs.get("id_consommable", getattr(self.instance, "id_consommable", None))
        quantite = attrs.get("quantite", getattr(self.instance, "quantite", None))
        destination_type = attrs.get("destination_type", getattr(self.instance, "destination_type", None))
        departement = attrs.get("id_departement", getattr(self.instance, "id_departement", None))
        direction = attrs.get("id_direction", getattr(self.instance, "id_direction", None))

        destination_type = (destination_type or Consommation.DestinationType.DEPARTEMENT).upper()
        attrs["destination_type"] = destination_type

        if self.instance and ("id_consommable" in attrs or "quantite" in attrs):
            raise serializers.ValidationError(
                "Une consommation deja enregistree ne peut pas modifier le stock. Creez une correction."
            )
        if consommable and quantite and consommable.quantite_stock < Decimal(quantite):
            raise serializers.ValidationError({"quantite": "Stock insuffisant pour cette consommation."})

        if destination_type not in Consommation.DestinationType.values:
            raise serializers.ValidationError(
                {"destination_type": "La destination doit etre DEPARTEMENT ou DIRECTION."}
            )

        if not departement:
            raise serializers.ValidationError({"id_departement": "Le departement destinataire est obligatoire."})

        if destination_type == Consommation.DestinationType.DIRECTION and not direction:
            raise serializers.ValidationError({"id_direction": "La direction destinataire est obligatoire."})

        if direction and direction.id_departement_id != departement.id_departement:
            raise serializers.ValidationError(
                {"id_direction": "La direction doit appartenir au departement choisi."}
            )

        if destination_type == Consommation.DestinationType.DEPARTEMENT:
            attrs["id_direction"] = None
        attrs["id_service"] = None

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            consommation = super().create(validated_data)
            consommable = consommation.id_consommable
            consommable.quantite_stock -= Decimal(consommation.quantite)
            consommable.save(update_fields=["quantite_stock"])
            return consommation
