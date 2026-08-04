from django.db import migrations, models


def split_state_and_stock_status(apps, schema_editor):
    Materiel = apps.get_model("stock", "Materiel")
    Affectation = apps.get_model("operations", "Affectation")
    active_material_ids = set(
        Affectation.objects.filter(statut="ACTIVE").values_list("id_materiel_id", flat=True)
    )

    for materiel in Materiel.objects.all().iterator():
        old_etat = materiel.etat

        if old_etat == "AFFECTE" or materiel.pk in active_material_ids:
            materiel.statut_stock = "AFFECTE"
        elif old_etat == "EN_STOCK" or materiel.id_magasin_id:
            materiel.statut_stock = "EN_STOCK"
        else:
            materiel.statut_stock = "HORS_STOCK"

        if old_etat in {"AFFECTE", "EN_STOCK"}:
            materiel.etat = "BON"

        materiel.save(update_fields=["etat", "statut_stock"])


def merge_state_and_stock_status(apps, schema_editor):
    Materiel = apps.get_model("stock", "Materiel")
    for materiel in Materiel.objects.all().iterator():
        if materiel.statut_stock in {"AFFECTE", "EN_STOCK"}:
            materiel.etat = materiel.statut_stock
            materiel.save(update_fields=["etat"])


class Migration(migrations.Migration):
    dependencies = [
        ("operations", "0005_alter_affectation_entite_type_and_more"),
        ("stock", "0002_magasin_id_direction_alter_materiel_etat"),
    ]

    operations = [
        migrations.AddField(
            model_name="materiel",
            name="statut_stock",
            field=models.CharField(
                choices=[
                    ("EN_STOCK", "En stock"),
                    ("AFFECTE", "Affecte"),
                    ("HORS_STOCK", "Hors stock"),
                ],
                default="EN_STOCK",
                max_length=20,
            ),
        ),
        migrations.RunPython(split_state_and_stock_status, merge_state_and_stock_status),
        migrations.AlterField(
            model_name="materiel",
            name="etat",
            field=models.CharField(
                choices=[
                    ("NEUF", "Neuf"),
                    ("BON", "Bon etat"),
                    ("EN_PANNE", "En panne"),
                    ("EN_REPARATION", "En reparation"),
                    ("HORS_SERVICE", "Hors service"),
                ],
                default="NEUF",
                max_length=20,
            ),
        ),
    ]
