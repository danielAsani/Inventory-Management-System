from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.core.serializer_validators import SanitizedModelSerializer, clean_text, validate_not_blank
from .models import Role, Users


class RoleSerializer(SanitizedModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
        extra_kwargs = {
            "code_role": {
                "validators": [
                    UniqueValidator(
                        queryset=Role.objects.all(),
                        message="Ce code role existe deja.",
                    )
                ]
            }
        }

    def validate_code_role(self, value):
        return validate_not_blank(value, "Le code du role ne peut pas etre vide.")

    def validate_nom_role(self, value):
        return validate_not_blank(value, "Le nom du role ne peut pas etre vide.")


class UsersSerializer(SanitizedModelSerializer):
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)

    class Meta:
        model = Users
        exclude = ["password_hash"]
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
        }

    def validate_email(self, value):
        if value:
            value = clean_text(value)
            validator = serializers.EmailField(
                error_messages={"invalid": "L'adresse email n'est pas valide."}
            )
            return validator.run_validation(value)
        return value

    def validate_matricule(self, value):
        return validate_not_blank(value, "Le matricule ne peut pas etre vide.")

    def validate_nom_users(self, value):
        return validate_not_blank(value, "Le nom de l'utilisateur ne peut pas etre vide.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError({"password": "Le mot de passe est obligatoire."})

        role = attrs.get("id_role") or getattr(self.instance, "id_role", None)
        scope_type = attrs.get("scope_type") or getattr(self.instance, "scope_type", None)

        if role and role.code_role not in {"ADMIN", "GESTION", "MAGASIN"}:
            raise serializers.ValidationError(
                {"id_role": "Seuls les roles ADMIN, GESTION et MAGASIN sont autorises."}
            )

        if role and role.code_role in {"ADMIN", "MAGASIN"}:
            attrs["scope_type"] = Users.ScopeType.GENERAL
            attrs["id_departement"] = None
            attrs["id_direction"] = None
            attrs["id_service"] = None
            attrs["id_magasin"] = None

            if role.code_role == "MAGASIN":
                queryset = Users.objects.filter(
                    id_role=role,
                    scope_type=Users.ScopeType.GENERAL,
                    statut=True,
                )
                if self.instance:
                    queryset = queryset.exclude(pk=self.instance.pk)
                if attrs.get("statut", getattr(self.instance, "statut", True)) and queryset.exists():
                    raise serializers.ValidationError(
                        {"id_role": "Il ne peut y avoir qu'un seul utilisateur MAGASIN actif."}
                    )

            return attrs

        scope_fields = {
            Users.ScopeType.DEPARTEMENT: "id_departement",
            Users.ScopeType.DIRECTION: "id_direction",
            Users.ScopeType.SERVICE: "id_service",
            Users.ScopeType.MAGASIN: "id_magasin",
        }

        if scope_type == Users.ScopeType.GENERAL:
            for field_name in scope_fields.values():
                attrs[field_name] = None
            return attrs

        required_field = scope_fields.get(scope_type)
        if required_field:
            value = attrs.get(required_field) or getattr(self.instance, required_field, None)
            if not value:
                raise serializers.ValidationError({required_field: "Ce champ est obligatoire pour ce perimetre."})
            for field_name in scope_fields.values():
                if field_name != required_field:
                    attrs[field_name] = None

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data["password_hash"] = make_password(password)
        return Users.objects.create(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            validated_data["password_hash"] = make_password(password)
        return super().update(instance, validated_data)
