from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.core.serializer_validators import (
    SanitizedModelSerializer,
    clean_text,
    validate_not_blank,
    validate_unique_optional_text,
    validate_unique_text,
)
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
        value = validate_not_blank(value, "Le nom du role ne peut pas etre vide.")
        return validate_unique_text(
            Role,
            "nom_role",
            value,
            "Un role avec ce nom existe deja.",
            self.instance,
        )


class UsersSerializer(SanitizedModelSerializer):
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)
    role = serializers.SerializerMethodField()
    role_libelle = serializers.SerializerMethodField()
    perimetre = serializers.SerializerMethodField()

    class Meta:
        model = Users
        exclude = ["groups", "user_permissions"]
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
            "matricule": {"required": False, "allow_blank": True},
            "last_login": {"read_only": True},
            "is_superuser": {"read_only": True},
            "is_staff": {"read_only": True},
            "date_joined": {"read_only": True},
        }

    def get_role(self, obj):
        return obj.role_code

    def get_role_libelle(self, obj):
        if not obj.id_role:
            return "-"
        return f"{obj.id_role.nom_role} ({obj.id_role.code_role})"

    def get_perimetre(self, obj):
        if obj.scope_type == Users.ScopeType.GENERAL:
            return "General"
        if obj.scope_type == Users.ScopeType.DEPARTEMENT and obj.id_departement:
            return f"Departement: {obj.id_departement.nom_departement}"
        if obj.scope_type == Users.ScopeType.DIRECTION and obj.id_direction:
            return f"Direction: {obj.id_direction.nom_direction}"
        return obj.scope_type or "-"

    def validate_email(self, value):
        if value:
            value = clean_text(value)
            validator = serializers.EmailField(
                error_messages={"invalid": "L'adresse email n'est pas valide."}
            )
            value = validator.run_validation(value)
            return validate_unique_optional_text(
                Users,
                "email",
                value,
                "Cette adresse email existe deja.",
                self.instance,
            )
        return value

    def validate_matricule(self, value):
        value = validate_not_blank(value, "Le matricule ne peut pas etre vide.").upper()
        return validate_unique_text(
            Users,
            "matricule",
            value,
            "Ce matricule existe deja.",
            self.instance,
        )

    def validate_nom_users(self, value):
        return validate_not_blank(value, "Le nom de l'utilisateur ne peut pas etre vide.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError({"password": "Le mot de passe est obligatoire."})

        role = attrs.get("id_role") or getattr(self.instance, "id_role", None)
        scope_type = attrs.get("scope_type") or getattr(self.instance, "scope_type", None)
        departement = attrs.get("id_departement") or getattr(self.instance, "id_departement", None)
        direction = attrs.get("id_direction") or getattr(self.instance, "id_direction", None)

        if role and role.code_role not in {"ADMIN", "GESTION", "MAGASIN"}:
            raise serializers.ValidationError(
                {"id_role": "Seuls les roles ADMIN, GESTION et MAGASIN sont autorises."}
            )

        if role and role.code_role in {"ADMIN", "MAGASIN"}:
            attrs["scope_type"] = Users.ScopeType.GENERAL
            attrs["id_departement"] = None
            attrs["id_direction"] = None
            attrs["id_service"] = None

            if role.code_role == "MAGASIN":
                queryset = Users.objects.filter(
                    id_role=role,
                    scope_type=Users.ScopeType.GENERAL,
                    is_active=True,
                )
                if self.instance:
                    queryset = queryset.exclude(pk=self.instance.pk)
                if attrs.get("is_active", getattr(self.instance, "is_active", True)) and queryset.exists():
                    raise serializers.ValidationError(
                        {"id_role": "Il ne peut y avoir qu'un seul utilisateur MAGASIN actif."}
                    )

            return attrs

        scope_fields = {
            Users.ScopeType.DEPARTEMENT: "id_departement",
            Users.ScopeType.DIRECTION: "id_direction",
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

        if scope_type == Users.ScopeType.DEPARTEMENT and departement:
            attrs["matricule"] = departement.code_departement.upper()
        elif scope_type == Users.ScopeType.DIRECTION and direction:
            attrs["matricule"] = direction.code_direction.upper()
        elif attrs.get("matricule"):
            attrs["matricule"] = clean_text(attrs["matricule"]).upper()
        elif self.instance is None:
            raise serializers.ValidationError({"matricule": "Le matricule est obligatoire."})

        if attrs.get("matricule"):
            queryset = Users.objects.filter(matricule__iexact=attrs["matricule"])
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({"matricule": "Ce code est deja utilise comme matricule."})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = Users(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
