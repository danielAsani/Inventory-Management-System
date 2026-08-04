from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="type_document",
            field=models.CharField(
                choices=[
                    ("FACTURE", "Facture"),
                    ("BON_LIVRAISON", "Bon de livraison"),
                    ("GARANTIE", "Garantie"),
                    ("FICHE_TECHNIQUE", "Fiche technique"),
                    ("AUTRE", "Autre"),
                ],
                default="AUTRE",
                max_length=100,
            ),
        ),
    ]
