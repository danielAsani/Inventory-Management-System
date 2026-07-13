from rest_framework import serializers

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    validate_not_blank,
    validate_not_future,
    validate_not_negative,
)
from .models import Document


class DocumentSerializer(SanitizedModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"

    def validate_type_document(self, value):
        return validate_not_blank(value, "Le type de document ne peut pas etre vide.")

    def validate_titre(self, value):
        return validate_not_blank(value, "Le titre du document ne peut pas etre vide.")

    def validate_taille_fichier_octets(self, value):
        return validate_not_negative(value, "La taille du fichier ne peut pas etre negative.")

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
        return attrs
