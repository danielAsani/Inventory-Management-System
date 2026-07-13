import os

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError

from apps.comptes.models import Role, Users
from apps.organisation.models import Departement, Direction, Service


INITIAL_USERS = [
    {
        "matricule": "ADMIN001",
        "email": "admin@example.com",
        "nom_users": "Administrateur Systeme",
        "role": "ADMIN",
        "scope_type": "GENERAL",
    },
    {
        "matricule": "GEST001",
        "email": "direction@example.com",
        "nom_users": "Direction demandeuse",
        "role": "GESTION",
        "scope_type": "DIRECTION",
    },
    {
        "matricule": "DEP001",
        "email": "departement@example.com",
        "nom_users": "Departement validateur",
        "role": "GESTION",
        "scope_type": "DEPARTEMENT",
    },
    {
        "matricule": "MAG001",
        "email": "magasin@example.com",
        "nom_users": "Magasin general",
        "role": "MAGASIN",
        "scope_type": "GENERAL",
    },
]

ROLE_NAMES = {
    "ADMIN": "Administrateur",
    "GESTION": "Gestion",
    "MAGASIN": "Magasin",
}

LEGACY_ROLE_CODES = {"GESTIONNAIRE", "MAGASINIER", "AUDITEUR"}
LEGACY_USER_MATRICULES = {"AUD001"}


class Command(BaseCommand):
    help = "Cree ou met a jour les comptes initiaux ADMIN/GESTION/MAGASIN."

    def add_arguments(self, parser):
        parser.add_argument("--password", default=os.getenv("INITIAL_USER_PASSWORD"))

    def handle(self, *args, **options):
        if not options["password"]:
            raise CommandError(
                "Definissez INITIAL_USER_PASSWORD ou passez --password pour creer les comptes initiaux."
            )

        password_hash = make_password(options["password"])
        organisation = self._get_or_create_default_organisation()

        for item in INITIAL_USERS:
            role = self._get_or_create_role(item["role"])
            user = Users.objects.filter(matricule=item["matricule"]).first()
            scope_fields = self._scope_fields(item, organisation)

            if user:
                user.email = item["email"]
                user.nom_users = item["nom_users"]
                user.password_hash = password_hash
                user.statut = True
                user.id_role = role
                user.scope_type = item["scope_type"]
                user.id_departement = scope_fields["id_departement"]
                user.id_direction = scope_fields["id_direction"]
                user.id_service = scope_fields["id_service"]
                user.id_magasin = scope_fields["id_magasin"]
                user.save()
                self.stdout.write(self.style.SUCCESS(f"{item['matricule']} mis a jour."))
                continue

            self._insert_user(item, role, password_hash, scope_fields)
            self.stdout.write(self.style.SUCCESS(f"{item['matricule']} cree."))

        self._disable_legacy_roles_and_users()

    def _get_or_create_role(self, expected_role):
        role = Role.objects.filter(code_role__iexact=expected_role).first()
        if role:
            role.nom_role = ROLE_NAMES.get(expected_role, role.nom_role)
            role.statut = True
            role.save(update_fields=["nom_role", "statut"])
            return role

        return Role.objects.create(
            code_role=expected_role,
            nom_role=ROLE_NAMES.get(expected_role, expected_role.title()),
            description=f"Role {expected_role} actif dans l'application.",
            statut=True,
        )

    def _disable_legacy_roles_and_users(self):
        Users.objects.filter(matricule__in=LEGACY_USER_MATRICULES).update(statut=False)
        Role.objects.filter(code_role__in=LEGACY_ROLE_CODES).update(statut=False)

    def _get_or_create_default_organisation(self):
        departement, _ = Departement.objects.update_or_create(
            code_departement="DOP",
            defaults={
                "nom_departement": "Departement Operations Techniques",
                "abreviation": "DOP",
                "statut": True,
            },
        )
        direction, _ = Direction.objects.update_or_create(
            code_direction="DEX",
            id_departement=departement,
            defaults={
                "nom_direction": "Direction Exploitation",
                "abreviation": "DEX",
                "statut": True,
            },
        )
        service, _ = Service.objects.update_or_create(
            code_service="SCO",
            id_direction=direction,
            defaults={
                "nom_service": "Service conduite des operations",
                "abreviation": "SCO",
                "statut": True,
            },
        )
        return {
            "departement": departement,
            "direction": direction,
            "service": service,
        }

    def _scope_fields(self, item, organisation):
        fields = {
            "id_departement": None,
            "id_direction": None,
            "id_service": None,
            "id_magasin": None,
        }
        if item["scope_type"] == "DEPARTEMENT":
            fields["id_departement"] = organisation["departement"]
        if item["scope_type"] == "DIRECTION":
            fields["id_direction"] = organisation["direction"]
        if item["scope_type"] == "SERVICE":
            fields["id_service"] = organisation["service"]
        return fields

    def _insert_user(self, item, role, password_hash, scope_fields):
        Users.objects.create(
            email=item["email"],
            nom_users=item["nom_users"],
            matricule=item["matricule"],
            telephone="000000000",
            password_hash=password_hash,
            statut=True,
            id_role=role,
            scope_type=item["scope_type"],
            **scope_fields,
        )
