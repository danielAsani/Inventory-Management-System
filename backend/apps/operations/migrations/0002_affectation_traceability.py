from django.db import migrations, models


TRACEABILITY_TYPE_PREFIXES = {
    "DEPARTEMENT": "DEP",
    "DIRECTION": "DIR",
    "SERVICE": "SER",
    "UTILISATEUR": "USR",
    "MAGASIN": "MAG",
}


def normalize_traceability_token(value):
    return "".join(character for character in str(value or "").upper() if character.isalnum() or character == "-")


def build_traceability_values(affectation, suffix=None):
    materiel_code = normalize_traceability_token(affectation.id_materiel.code_materiel)
    entite_prefix = TRACEABILITY_TYPE_PREFIXES.get(
        affectation.entite_type,
        normalize_traceability_token(affectation.entite_type)[:3],
    )
    date_value = affectation.date_affectation
    base = f"AFF-{materiel_code}-{entite_prefix}{affectation.entite_id}-{date_value:%Y%m%d}"
    if suffix:
        base = f"{base}-{suffix:02d}"
    return {
        "code_affectation": base,
        "code_barre": base,
        "qr_code": f"AFF|{base}|MAT:{materiel_code}|TO:{affectation.entite_type}:{affectation.entite_id}|DATE:{date_value:%Y-%m-%d}",
    }


def populate_traceability(apps, schema_editor):
    Affectation = apps.get_model("operations", "Affectation")
    used_values = set()

    for affectation in Affectation.objects.select_related("id_materiel").order_by("id_affectation"):
        suffix = None
        while True:
            values = build_traceability_values(affectation, suffix)
            candidate_values = set(values.values())
            if not used_values.intersection(candidate_values):
                used_values.update(candidate_values)
                for field_name, value in values.items():
                    setattr(affectation, field_name, value)
                affectation.save(update_fields=["code_affectation", "code_barre", "qr_code"])
                break
            suffix = 1 if suffix is None else suffix + 1


class Migration(migrations.Migration):

    dependencies = [
        ("operations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="affectation",
            name="code_affectation",
            field=models.CharField(blank=True, max_length=80, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="affectation",
            name="code_barre",
            field=models.CharField(blank=True, max_length=80, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="affectation",
            name="qr_code",
            field=models.CharField(blank=True, max_length=190, null=True, unique=True),
        ),
        migrations.RunPython(populate_traceability, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="affectation",
            name="entite_type",
            field=models.CharField(
                choices=[
                    ("DEPARTEMENT", "DÃ©partement"),
                    ("DIRECTION", "Direction"),
                    ("SERVICE", "Service"),
                    ("UTILISATEUR", "Utilisateur"),
                    ("MAGASIN", "Magasin"),
                ],
                max_length=20,
            ),
        ),
    ]
