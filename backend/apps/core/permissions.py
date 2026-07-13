from rest_framework.permissions import SAFE_METHODS, BasePermission


ROLE_ADMIN = "ADMIN"
ROLE_GESTION = "GESTION"
ROLE_MAGASIN = "MAGASIN"


class RoleBasedPermission(BasePermission):
    message = "Vous n'avez pas la permission d'effectuer cette action."

    def has_permission(self, request, view):
        if request.method == "OPTIONS":
            return True

        user = request.user
        if not user or not getattr(user, "is_authenticated", False):
            self.message = "Token manquant."
            return False

        role = getattr(user, "role_code", None)
        if not role:
            self.message = "Role utilisateur introuvable ou inactif."
            return False

        if role == ROLE_ADMIN:
            return True

        allowed_roles = self._allowed_roles_for_request(request, view)
        return role in allowed_roles

    def _allowed_roles_for_request(self, request, view):
        action = getattr(view, "action", None)
        permissions = getattr(view, "role_permissions", {})

        if action in permissions:
            return permissions[action]

        if request.method in SAFE_METHODS:
            return permissions.get("read", set())

        return permissions.get("write", set())


READ_ALL_ROLES = {ROLE_ADMIN, ROLE_GESTION, ROLE_MAGASIN}
GESTION_WRITE_ROLES = {ROLE_ADMIN, ROLE_GESTION}
MAGASIN_WRITE_ROLES = {ROLE_ADMIN, ROLE_MAGASIN}
OPERATION_WRITE_ROLES = GESTION_WRITE_ROLES
