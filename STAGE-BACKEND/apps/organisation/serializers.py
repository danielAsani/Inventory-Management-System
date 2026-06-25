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
                        message="Ce code département existe déjà.",
                    )
                ]
            }
        }

    def validate_code_departement(self, value):
        return validate_not_blank(value, "Le code du département ne peut pas être vide.")

    def validate_nom_departement(self, value):
        return validate_not_blank(value, "Le nom du département ne peut pas être vide.")


class DirectionSerializer(SanitizedModelSerializer):
    class Meta:
        model = Direction
        fields = "__all__"
        extra_kwargs = {
            "code_direction": {
                "validators": [
                    UniqueValidator(
                        queryset=Direction.objects.all(),
                        message="Ce code direction existe déjà.",
                    )
                ]
            }
        }

    def validate_code_direction(self, value):
        return validate_not_blank(value, "Le code de la direction ne peut pas être vide.")

    def validate_nom_direction(self, value):
        return validate_not_blank(value, "Le nom de la direction ne peut pas être vide.")


class ServiceSerializer(SanitizedModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"
        extra_kwargs = {
            "code_service": {
                "validators": [
                    UniqueValidator(
                        queryset=Service.objects.all(),
                        message="Ce code service existe déjà.",
                    )
                ]
            }
        }

    def validate_code_service(self, value):
        return validate_not_blank(value, "Le code du service ne peut pas être vide.")

    def validate_nom_service(self, value):
        return validate_not_blank(value, "Le nom du service ne peut pas être vide.")
