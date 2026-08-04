from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0003_remove_document_file_metadata"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="chemin_fichier",
            field=models.FileField(blank=True, max_length=500, null=True, upload_to="documents/"),
        ),
    ]
