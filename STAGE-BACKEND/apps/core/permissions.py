from rest_framework.permissions import SAFE_METHODS, BasePermission


ROLE_ADMIN = 'ADMIN'
ROLE_GESTIONNAIRE = 'GESTIONNAIRE'
ROLE_MAGASINIER = 'MAGASINIER'
ROLE_AUDITEUR = 'AUDITEUR'


class RoleBasedPermission(BasePermission):
    message = "Vous n'avez pas la permission d'effectuer cette action."

    def has_permission(self, request, view):
        # TODO: appliquer le filtrage par SCOPE_TYPE dans get_queryset()
        # module par module quand la relation Oracle est claire.
        user = request.user
        if not user or not getattr(user, 'is_authenticated', False):
            self.message = 'Token manquant.'
            return False

        role = getattr(user, 'role_code', None)
        if not role:
            self.message = 'Rôle utilisateur introuvable ou inactif.'
            return False

        if role == ROLE_ADMIN:
            return True

        if role == ROLE_AUDITEUR:
            return request.method in SAFE_METHODS

        allowed_roles = self._allowed_roles_for_request(request, view)
        return role in allowed_roles

    def _allowed_roles_for_request(self, request, view):
        action = getattr(view, 'action', None)
        permissions = getattr(view, 'role_permissions', {})

        if action in permissions:
            return permissions[action]

        if request.method in SAFE_METHODS:
            return permissions.get('read', set())

        return permissions.get('write', set())


READ_ALL_ROLES = {ROLE_ADMIN, ROLE_GESTIONNAIRE, ROLE_MAGASINIER, ROLE_AUDITEUR}
GESTIONNAIRE_WRITE_ROLES = {ROLE_ADMIN, ROLE_GESTIONNAIRE}
MAGASINIER_CREATE_ROLES = {ROLE_ADMIN, ROLE_MAGASINIER}
