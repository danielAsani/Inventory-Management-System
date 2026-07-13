
from django.db import migrations, models


def normalize_roles(apps, schema_editor):
    Role = apps.get_model("comptes", "Role")
    Users = apps.get_model("comptes", "Users")

    def ensure_role(code, name):
        role, _ = Role.objects.get_or_create(
            code_role=code,
            defaults={
                "nom_role": name,
                "description": f"Role {name} actif dans l'application.",
                "statut": True,
            },
        )
        role.nom_role = name
        role.statut = True
        role.save(update_fields=["nom_role", "statut"])
        return role

    ensure_role("ADMIN", "Administrateur")

    role_mappings = {
        "GESTIONNAIRE": ("GESTION", "Gestion"),
        "MAGASINIER": ("MAGASIN", "Magasin"),
    }

    for old_code, (new_code, new_name) in role_mappings.items():
        new_role = Role.objects.filter(code_role=new_code).first()
        old_role = Role.objects.filter(code_role=old_code).first()

        if old_role and not new_role:
            old_role.code_role = new_code
            old_role.nom_role = new_name
            old_role.statut = True
            old_role.save(update_fields=["code_role", "nom_role", "statut"])
            continue

        if not new_role:
            new_role = ensure_role(new_code, new_name)

        if old_role:
            Users.objects.filter(id_role=old_role).update(id_role=new_role)
            old_role.delete()

    auditeur = Role.objects.filter(code_role="AUDITEUR").first()
    if auditeur:
        Users.objects.filter(id_role=auditeur).delete()
        auditeur.delete()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('comptes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(normalize_roles, noop_reverse),
        migrations.AlterField(
            model_name='role',
            name='code_role',
            field=models.CharField(choices=[('ADMIN', 'Administrateur'), ('GESTION', 'Gestion'), ('MAGASIN', 'Magasin')], max_length=20, unique=True),
        ),
    ]
