from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone

from apps.comptes.models import Role, Users


TEST_USERS = [
    {
        "matricule": "GEST001",
        "email": "gest@snel.cd",
        "nom_users": "Gestionnaire SNEL",
        "role": "GESTIONNAIRE",
    },
    {
        "matricule": "MAG001",
        "email": "magasinier@snel.cd",
        "nom_users": "Magasinier SNEL",
        "role": "MAGASINIER",
    },
    {
        "matricule": "AUD001",
        "email": "auditeur@snel.cd",
        "nom_users": "Auditeur SNEL",
        "role": "AUDITEUR",
    },
]


class Command(BaseCommand):
    help = "Crée ou met à jour les utilisateurs de test SNEL avec un password_hash Django."

    def add_arguments(self, parser):
        parser.add_argument("--password", default="Test@123")

    def handle(self, *args, **options):
        password_hash = make_password(options["password"])

        for item in TEST_USERS:
            role = self._get_role(item["role"])
            user = Users.objects.filter(matricule=item["matricule"]).first()

            if user:
                user.email = item["email"]
                user.nom_users = item["nom_users"]
                user.password_hash = password_hash
                user.statut = True
                user.id_role = role
                user.scope_type = "CENTRAL"
                user.save()
                self.stdout.write(self.style.SUCCESS(f"{item['matricule']} mis à jour."))
                continue

            self._insert_user(item, role, password_hash)
            self.stdout.write(self.style.SUCCESS(f"{item['matricule']} créé."))

    def _get_role(self, expected_role):
        role = Role.objects.filter(code_role__iexact=expected_role, statut=True).first()
        if role:
            return role

        role = Role.objects.filter(nom_role__icontains=expected_role, statut=True).first()
        if role:
            return role

        raise CommandError(f"Rôle actif introuvable pour {expected_role}.")

    def _insert_user(self, item, role, password_hash):
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
                    SCOPE_TYPE
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
                    :scope_type
                )
                """,
                {
                    "email": item["email"],
                    "nom_users": item["nom_users"],
                    "matricule": item["matricule"],
                    "telephone": "000000000",
                    "password_hash": password_hash,
                    "statut": 1,
                    "date_ajout": timezone.localdate(),
                    "id_role": role.id_role,
                    "scope_type": "CENTRAL",
                },
            )
