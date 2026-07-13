from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Document(models.Model):
    class TypeDocument(models.TextChoices):
        FACTURE = "FACTURE", "Facture"
        BON_LIVRAISON = "BON_LIVRAISON", "Bon de livraison"
        GARANTIE = "GARANTIE", "Garantie"
        FICHE_TECHNIQUE = "FICHE_TECHNIQUE", "Fiche technique"
        PHOTO = "PHOTO", "Photo"
        AUTRE = "AUTRE", "Autre"

    id_document = models.AutoField(primary_key=True)

    id_materiel = models.ForeignKey(
        "stock.Materiel",
        on_delete=models.PROTECT,
        db_column="id_materiel",
        blank=True,
        null=True,
        related_name="documents"
    )

    id_consommable = models.ForeignKey(
        "stock.Consommable",
        on_delete=models.PROTECT,
        db_column="id_consommable",
        blank=True,
        null=True,
        related_name="documents"
    )

    cree_par = models.ForeignKey(
        "comptes.Users",
        on_delete=models.PROTECT,
        db_column="cree_par",
        related_name="documents_crees"
    )

    type_document = models.CharField(
        max_length=100,
        choices=TypeDocument.choices,
        default=TypeDocument.AUTRE
    )

    numero_document = models.CharField(max_length=100, blank=True, null=True)
    titre = models.CharField(max_length=255)

    chemin_fichier = models.CharField(max_length=500, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    taille_fichier_octets = models.PositiveBigIntegerField(blank=True, null=True)

    date_upload = models.DateTimeField(default=timezone.now)
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "document"

    def clean(self):
        if not self.id_materiel and not self.id_consommable:
            raise ValidationError(
                "Le document doit être lié soit à un matériel, soit à un consommable."
            )

        if self.id_materiel and self.id_consommable:
            raise ValidationError(
                "Le document ne peut pas être lié à un matériel et à un consommable en même temps."
            )

    def __str__(self):
        return self.titre