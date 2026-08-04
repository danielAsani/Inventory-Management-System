from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_not_blank,
    validate_not_future,
)
from .models import Document


class DocumentSerializer(SanitizedModelSerializer):
    article = serializers.SerializerMethodField()
    article_type = serializers.SerializerMethodField()
    cree_par_nom = serializers.CharField(source="cree_par.nom_users", read_only=True)

    class Meta:
        model = Document
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

    def validate_type_document(self, value):
        return validate_not_blank(value, "Le type de document ne peut pas etre vide.")

    def validate_titre(self, value):
        return validate_not_blank(value, "Le titre du document ne peut pas etre vide.")

    def validate_chemin_fichier(self, value):
        file_name = getattr(value, "name", value)
        if file_name and not str(file_name).lower().endswith(".pdf"):
            raise serializers.ValidationError("Le document doit etre un fichier PDF.")
        content_type = getattr(value, "content_type", "")
        if content_type and content_type != "application/pdf":
            raise serializers.ValidationError("Le document doit etre un fichier PDF.")
        return value

    def validate_date_upload(self, value):
        return validate_not_future(value, "La date d'envoi du document ne peut pas etre dans le futur.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        materiel = attrs.get("id_materiel", getattr(self.instance, "id_materiel", None))
        consommable = attrs.get("id_consommable", getattr(self.instance, "id_consommable", None))

        if not materiel and not consommable:
            raise serializers.ValidationError(
                "Le document doit etre lie soit a un materiel, soit a un consommable."
            )
        if materiel and consommable:
            raise serializers.ValidationError(
                "Le document ne peut pas etre lie a un materiel et a un consommable en meme temps."
            )
        type_document = attrs.get("type_document", getattr(self.instance, "type_document", None))
        numero_document = attrs.get("numero_document", getattr(self.instance, "numero_document", None))
        if type_document and numero_document:
            queryset = Document.objects.filter(
                type_document=type_document,
                numero_document__iexact=numero_document,
            )
            if materiel:
                queryset = queryset.filter(id_materiel=materiel)
            if consommable:
                queryset = queryset.filter(id_consommable=consommable)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"numero_document": "Ce numero de document existe deja pour cet article et ce type."}
                )
        return attrs
