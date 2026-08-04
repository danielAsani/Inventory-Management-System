import os

from apps.comptes.models import Role, Users


DEFAULT_ORG_PASSWORD = "Default@2026"


def default_org_password():
    return os.getenv("INITIAL_USER_PASSWORD") or os.getenv("ORG_DEFAULT_USER_PASSWORD") or DEFAULT_ORG_PASSWORD


def gestion_role():
    role, _ = Role.objects.get_or_create(
        code_role=Role.RoleCode.GESTION,
        defaults={
            "nom_role": "Gestion",
            "description": "Compte de gestion cree automatiquement.",
            "statut": True,
        },
    )
    if not role.statut:
        role.statut = True
        role.save(update_fields=["statut"])
    return role


def _matricule(prefix, *codes):
    clean_codes = [str(code or "").upper().replace(" ", "") for code in codes if code]
    return (clean_codes[-1] if clean_codes else str(prefix or "").upper())[:30]


def _scoped_account(matricule, scope_field, scope_value, defaults):
    target = Users.objects.filter(matricule__iexact=matricule).first()
    if target and getattr(target, f"{scope_field}_id") == getattr(scope_value, f"{scope_field}", scope_value.pk):
        return target, False
    if target:
        raise ValueError(f"Le matricule {matricule} est deja utilise par un autre compte.")

    return Users.objects.create(matricule=matricule, **defaults), True


def ensure_department_account(departement):
    matricule = _matricule("DEP", departement.code_departement)
    user, created = _scoped_account(
        matricule=matricule,
        scope_field="id_departement",
        scope_value=departement,
        defaults={
            "nom_users": departement.code_departement,
            "email": None,
            "telephone": "000000000",
            "id_role": gestion_role(),
            "scope_type": Users.ScopeType.DEPARTEMENT,
            "id_departement": departement,
            "is_active": departement.statut,
        },
    )
    if created:
        password = default_org_password()
        if password:
            user.set_password(password)
        user.save(update_fields=["password"])
        return user

    fields = []
    updates = {
        "nom_users": departement.code_departement,
        "id_role": gestion_role(),
        "scope_type": Users.ScopeType.DEPARTEMENT,
        "id_departement": departement,
        "id_direction": None,
        "id_service": None,
        "id_magasin": None,
        "is_active": departement.statut,
    }
    for field, value in updates.items():
        if getattr(user, field) != value:
            setattr(user, field, value)
            fields.append(field)
    if fields:
        user.save(update_fields=fields)
    return user


def ensure_direction_account(direction):
    departement_code = direction.id_departement.code_departement
    matricule = _matricule("DIR", departement_code, direction.code_direction)
    user, created = _scoped_account(
        matricule=matricule,
        scope_field="id_direction",
        scope_value=direction,
        defaults={
            "nom_users": direction.code_direction,
            "email": None,
            "telephone": "000000000",
            "id_role": gestion_role(),
            "scope_type": Users.ScopeType.DIRECTION,
            "id_direction": direction,
            "is_active": direction.statut and direction.id_departement.statut,
        },
    )
    if created:
        password = default_org_password()
        if password:
            user.set_password(password)
        user.save(update_fields=["password"])
        return user

    fields = []
    updates = {
        "nom_users": direction.code_direction,
        "id_role": gestion_role(),
        "scope_type": Users.ScopeType.DIRECTION,
        "id_departement": None,
        "id_direction": direction,
        "id_service": None,
        "id_magasin": None,
        "is_active": direction.statut and direction.id_departement.statut,
    }
    for field, value in updates.items():
        if getattr(user, field) != value:
            setattr(user, field, value)
            fields.append(field)
    if fields:
        user.save(update_fields=fields)
    return user
