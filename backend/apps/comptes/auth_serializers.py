from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.exceptions import TokenError

from apps.core.authentication import create_access_from_refresh, create_token_pair
from apps.core.serializer_validators import SanitizedModelSerializer, clean_text
from .models import Users


class InvalidCredentials(APIException):
    status_code = 401
    default_detail = "Identifiants invalides."
    default_code = "invalid_credentials"


class UserProfileSerializer(SanitizedModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            "id_users",
            "nom_users",
            "email",
            "matricule",
            "telephone",
            "role",
            "scope_type",
            "id_departement",
            "id_direction",
            "id_service",
            "id_magasin",
        ]

    def get_role(self, obj):
        return obj.role_code


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

        if not user.statut:
            raise serializers.ValidationError("Utilisateur inactif.")

        if not user.id_role or not user.id_role.statut:
            raise serializers.ValidationError("Role utilisateur introuvable ou inactif.")

        if not check_password(password, user.password_hash):
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
        except TokenError:
            raise serializers.ValidationError("Token invalide ou expire.")
        return attrs
