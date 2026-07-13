from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.core.serializer_validators import SanitizedModelSerializer, validate_not_blank
from .models import Departement, Direction, Service


class DepartementSerializer(SanitizedModelSerializer):
    class Meta:
        model = Departement
        fields = "__all__"
        extra_kwargs = {
            "code_departement": {
                "validators": [
                    UniqueValidator(
                        queryset=Departement.objects.all(),
                        message="Ce code departement existe deja.",
                    )
                ]
            }
        }

    def validate_code_departement(self, value):
        return validate_not_blank(value, "Le code du departement ne peut pas etre vide.")

    def validate_nom_departement(self, value):
        return validate_not_blank(value, "Le nom du departement ne peut pas etre vide.")


class DirectionSerializer(SanitizedModelSerializer):
    class Meta:
        model = Direction
        fields = "__all__"

    def validate_code_direction(self, value):
        return validate_not_blank(value, "Le code de la direction ne peut pas etre vide.")

    def validate_nom_direction(self, value):
        return validate_not_blank(value, "Le nom de la direction ne peut pas etre vide.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        code = attrs.get("code_direction") or getattr(self.instance, "code_direction", None)
        departement = attrs.get("id_departement") or getattr(self.instance, "id_departement", None)
        if code and departement:
            queryset = Direction.objects.filter(code_direction=code, id_departement=departement)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"code_direction": "Ce code direction existe deja dans ce departement."}
                )
        return attrs


class ServiceSerializer(SanitizedModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"

    def validate_code_service(self, value):
        return validate_not_blank(value, "Le code du service ne peut pas etre vide.")

    def validate_nom_service(self, value):
        return validate_not_blank(value, "Le nom du service ne peut pas etre vide.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        code = attrs.get("code_service") or getattr(self.instance, "code_service", None)
        direction = attrs.get("id_direction") or getattr(self.instance, "id_direction", None)
        if code and direction:
            queryset = Service.objects.filter(code_service=code, id_direction=direction)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"code_service": "Ce code service existe deja dans cette direction."}
                )
        return attrs
