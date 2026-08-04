from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("maintenance", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entretien",
            name="statut",
            field=models.CharField(
                choices=[
                    ("EN_COURS", "En cours"),
                    ("TERMINE", "Termine"),
                    ("ANNULE", "Annule"),
                ],
                default="EN_COURS",
                max_length=20,
            ),
        ),
    ]
