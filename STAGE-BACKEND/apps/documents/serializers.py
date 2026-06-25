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
        return validate_not_blank(value, "Le type de document ne peut pas être vide.")

    def validate_titre(self, value):
        return validate_not_blank(value, "Le titre du document ne peut pas être vide.")

    def validate_taille_fichier_octets(self, value):
        return validate_not_negative(value, "La taille du fichier ne peut pas être négative.")

    def validate_date_upload(self, value):
        return validate_not_future(value, "La date d'envoi du document ne peut pas être dans le futur.")
