from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.comptes.models import Users


def _scope_id(user, field_name):
    return getattr(user, f"{field_name}_id", None)


def add_user_claims(token, user):
    token["id_users"] = user.id_users
    token["matricule"] = user.matricule
    token["role"] = user.role_code
    token["scope_type"] = user.scope_type
    token["id_departement"] = _scope_id(user, "id_departement")
    token["id_direction"] = _scope_id(user, "id_direction")
    token["id_service"] = _scope_id(user, "id_service")
    token["id_magasin"] = _scope_id(user, "id_magasin")
    return token


def create_token_pair(user):
    refresh = RefreshToken()
    add_user_claims(refresh, user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def create_access_from_refresh(refresh_token):
    refresh = RefreshToken(refresh_token)
    user = get_active_user_from_payload(refresh)
    access = refresh.access_token
    add_user_claims(access, user)
    return str(access)


def get_active_user_from_payload(payload):
    try:
        user = Users.objects.select_related("id_role").get(id_users=payload.get("id_users"))
    except Users.DoesNotExist:
        raise AuthenticationFailed("Token invalide ou expire.")

    if not user.statut:
        raise AuthenticationFailed("Utilisateur inactif.")

    if not user.id_role or not user.id_role.statut:
        raise AuthenticationFailed("Role utilisateur introuvable ou inactif.")

    return user


class CustomTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate_header(self, request):
        return self.keyword

    def authenticate(self, request):
        try:
            auth_header = authentication.get_authorization_header(request).decode("utf-8")
        except UnicodeDecodeError:
            raise AuthenticationFailed("Token invalide ou expire.")

        if not auth_header:
            if request.method == "OPTIONS":
                return None
            raise AuthenticationFailed("Token manquant.")

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != self.keyword.lower():
            raise AuthenticationFailed("Token invalide ou expire.")

        try:
            payload = AccessToken(parts[1])
            user = get_active_user_from_payload(payload)
        except TokenError:
            raise AuthenticationFailed("Token invalide ou expire.")

        request.user_role = user.role_code
        return user, parts[1]
