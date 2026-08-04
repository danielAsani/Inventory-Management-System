from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    clean_text,
    validate_not_blank,
    validate_unique_optional_text,
    validate_unique_text,
)
from .accounts import ensure_department_account, ensure_direction_account
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
        value = validate_not_blank(value, "Le code du departement ne peut pas etre vide.").upper()
        return validate_unique_text(
            Departement,
            "code_departement",
            value,
            "Ce code departement existe deja.",
            self.instance,
        )

    def validate_nom_departement(self, value):
        value = validate_not_blank(value, "Le nom du departement ne peut pas etre vide.")
        return validate_unique_text(
            Departement,
            "nom_departement",
            value,
            "Un departement avec ce nom existe deja.",
            self.instance,
        )

    def validate_abreviation(self, value):
        if value in (None, ""):
            return value
        value = clean_text(value).upper()
        return validate_unique_optional_text(
            Departement,
            "abreviation",
            value,
            "Cette abreviation de departement existe deja.",
            self.instance,
        )

    def create(self, validated_data):
        departement = super().create(validated_data)
        ensure_department_account(departement)
        return departement

    def update(self, instance, validated_data):
        departement = super().update(instance, validated_data)
        ensure_department_account(departement)
        return departement


class DirectionSerializer(SanitizedModelSerializer):
    departement_nom = serializers.CharField(source="id_departement.nom_departement", read_only=True)

    class Meta:
        model = Direction
        fields = "__all__"

    def validate_code_direction(self, value):
        return validate_not_blank(value, "Le code de la direction ne peut pas etre vide.").upper()

    def validate_nom_direction(self, value):
        return validate_not_blank(value, "Le nom de la direction ne peut pas etre vide.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("abreviation"):
            attrs["abreviation"] = clean_text(attrs["abreviation"]).upper()
        code = attrs.get("code_direction") or getattr(self.instance, "code_direction", None)
        departement = attrs.get("id_departement") or getattr(self.instance, "id_departement", None)
        if code and departement:
            queryset = Direction.objects.filter(code_direction__iexact=code, id_departement=departement)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"code_direction": "Ce code direction existe deja dans ce departement."}
                )
        nom = attrs.get("nom_direction", getattr(self.instance, "nom_direction", None))
        if nom and departement:
            queryset = Direction.objects.filter(nom_direction__iexact=nom, id_departement=departement)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"nom_direction": "Une direction avec ce nom existe deja dans ce departement."}
                )
        abreviation = attrs.get("abreviation", getattr(self.instance, "abreviation", None))
        if abreviation and departement:
            queryset = Direction.objects.filter(abreviation__iexact=abreviation, id_departement=departement)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"abreviation": "Cette abreviation de direction existe deja dans ce departement."}
                )
        return attrs

    def create(self, validated_data):
        direction = super().create(validated_data)
        ensure_direction_account(direction)
        return direction

    def update(self, instance, validated_data):
        direction = super().update(instance, validated_data)
        ensure_direction_account(direction)
        return direction


class ServiceSerializer(SanitizedModelSerializer):
    direction_nom = serializers.CharField(source="id_direction.nom_direction", read_only=True)
    departement_nom = serializers.CharField(source="id_direction.id_departement.nom_departement", read_only=True)

    class Meta:
        model = Service
        fields = "__all__"

    def validate_code_service(self, value):
        return validate_not_blank(value, "Le code du service ne peut pas etre vide.").upper()

    def validate_nom_service(self, value):
        return validate_not_blank(value, "Le nom du service ne peut pas etre vide.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get("abreviation"):
            attrs["abreviation"] = clean_text(attrs["abreviation"]).upper()
        code = attrs.get("code_service") or getattr(self.instance, "code_service", None)
        direction = attrs.get("id_direction") or getattr(self.instance, "id_direction", None)
        if code and direction:
            queryset = Service.objects.filter(code_service__iexact=code, id_direction=direction)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"code_service": "Ce code service existe deja dans cette direction."}
                )
        nom = attrs.get("nom_service", getattr(self.instance, "nom_service", None))
        if nom and direction:
            queryset = Service.objects.filter(nom_service__iexact=nom, id_direction=direction)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"nom_service": "Un service avec ce nom existe deja dans cette direction."}
                )
        abreviation = attrs.get("abreviation", getattr(self.instance, "abreviation", None))
        if abreviation and direction:
            queryset = Service.objects.filter(abreviation__iexact=abreviation, id_direction=direction)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"abreviation": "Cette abreviation de service existe deja dans cette direction."}
                )
        return attrs
