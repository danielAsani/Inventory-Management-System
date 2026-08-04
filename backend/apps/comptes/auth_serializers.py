from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import password_validation

from apps.core.authentication import create_access_from_refresh, create_token_pair
from apps.core.serializer_validators import SanitizedModelSerializer, clean_text
from .models import Users


class InvalidCredentials(APIException):
    status_code = 401
    default_detail = "Identifiants invalides."
    default_code = "invalid_credentials"


class UserProfileSerializer(SanitizedModelSerializer):
    role = serializers.SerializerMethodField()
    role_libelle = serializers.SerializerMethodField()
    perimetre = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            "id_users",
            "nom_users",
            "email",
            "matricule",
            "telephone",
            "role",
            "role_libelle",
            "scope_type",
            "perimetre",
            "id_departement",
            "id_direction",
            "id_magasin",
        ]

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
        if obj.scope_type == Users.ScopeType.MAGASIN and obj.id_magasin:
            return f"Magasin: {obj.id_magasin.nom_magasin}"
        return obj.scope_type or "-"


class LoginSerializer(serializers.Serializer):
    matricule = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        matricule = clean_text(attrs.get("matricule"))
        email = clean_text(attrs.get("email"))
        password = attrs.get("password")

        if not matricule and not email:
            raise serializers.ValidationError("Le matricule ou l'email est obligatoire.")

        user = self._get_user(matricule, email)
        if not user:
            raise InvalidCredentials()

        if not user.is_active:
            raise serializers.ValidationError("Utilisateur inactif.")

        if not user.id_role or not user.id_role.statut:
            raise serializers.ValidationError("Role utilisateur introuvable ou inactif.")

        if not user.check_password(password):
            raise InvalidCredentials()

        attrs["user"] = user
        attrs["tokens"] = create_token_pair(user)
        return attrs

    def _get_user(self, matricule, email):
        queryset = Users.objects.select_related("id_role")
        if matricule:
            return queryset.filter(matricule=matricule).first()
        return queryset.filter(email__iexact=email).first()


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            attrs["access"] = create_access_from_refresh(attrs["refresh"])
        except (APIException, TokenError):
            raise serializers.ValidationError("Token invalide ou expire.")
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Les deux mots de passe ne correspondent pas."})

        password_validation.validate_password(attrs["new_password"], self.context["request"].user)
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user
