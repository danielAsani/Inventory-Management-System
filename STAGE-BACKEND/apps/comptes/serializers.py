from django.contrib.auth.hashers import make_password
from django.db import connection
from django.utils import timezone
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
                        message="Ce code rôle existe déjà.",
                    )
                ]
            }
        }

    def validate_code_role(self, value):
        return validate_not_blank(value, "Le code du rôle ne peut pas être vide.")

    def validate_nom_role(self, value):
        return validate_not_blank(value, "Le nom du rôle ne peut pas être vide.")


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
            validator = serializers.EmailField(error_messages={"invalid": "L'adresse email n'est pas valide."})
            return validator.run_validation(value)
        return value

    def validate_matricule(self, value):
        return validate_not_blank(value, "Le matricule ne peut pas être vide.")

    def validate_nom_users(self, value):
        return validate_not_blank(value, "Le nom de l'utilisateur ne peut pas être vide.")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError({"password": "Le mot de passe est obligatoire."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data["password_hash"] = make_password(password)
        return self._insert_user(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            validated_data["password_hash"] = make_password(password)
        return super().update(instance, validated_data)

    def _fk_id(self, validated_data, field_name):
        value = validated_data.get(field_name)
        return getattr(value, f"{field_name}_id", value.pk) if value else None

    def _insert_user(self, validated_data):
        # ID_USERS est GENERATED ALWAYS côté Oracle : on l'omet volontairement.
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO USERS (
                    EMAIL,
                    NOM_USERS,
                    MATRICULE,
                    TELEPHONE,
                    PASSWORD_HASH,
                    STATUT,
                    DATE_AJOUT,
                    ID_ROLE,
                    SCOPE_TYPE,
                    ID_DEPARTEMENT,
                    ID_DIRECTION,
                    ID_SERVICE,
                    ID_MAGASIN
                )
                VALUES (
                    :email,
                    :nom_users,
                    :matricule,
                    :telephone,
                    :password_hash,
                    :statut,
                    :date_ajout,
                    :id_role,
                    :scope_type,
                    :id_departement,
                    :id_direction,
                    :id_service,
                    :id_magasin
                )
                """,
                {
                    "email": validated_data.get("email"),
                    "nom_users": validated_data["nom_users"],
                    "matricule": validated_data["matricule"],
                    "telephone": validated_data.get("telephone"),
                    "password_hash": validated_data["password_hash"],
                    "statut": int(validated_data.get("statut", True)),
                    "date_ajout": validated_data.get("date_ajout") or timezone.localdate(),
                    "id_role": self._fk_id(validated_data, "id_role"),
                    "scope_type": validated_data.get("scope_type"),
                    "id_departement": self._fk_id(validated_data, "id_departement"),
                    "id_direction": self._fk_id(validated_data, "id_direction"),
                    "id_service": self._fk_id(validated_data, "id_service"),
                    "id_magasin": self._fk_id(validated_data, "id_magasin"),
                },
            )
        return Users.objects.get(matricule=validated_data["matricule"])
