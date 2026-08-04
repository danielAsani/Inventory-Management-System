from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_remove_photo_document_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="document",
            name="mime_type",
        ),
        migrations.RemoveField(
            model_name="document",
            name="taille_fichier_octets",
        ),
    ]
