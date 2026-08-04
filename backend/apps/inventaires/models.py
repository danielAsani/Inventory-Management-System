from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.core.code_generation import generate_prefixed_code


class Inventaire(models.Model):
    class EntiteType(models.TextChoices):
        DEPARTEMENT = "DEPARTEMENT", "Département"
        DIRECTION = "DIRECTION", "Direction"
        MAGASIN = "MAGASIN", "Magasin"

    class TypeInventaire(models.TextChoices):
        GENERAL = "GENERAL", "Général"
        PARTIEL = "PARTIEL", "Partiel"
        PERIODIQUE = "PERIODIQUE", "Périodique"
        EXCEPTIONNEL = "EXCEPTIONNEL", "Exceptionnel"

    class StatutInventaire(models.TextChoices):
        EN_COURS = "EN_COURS", "En cours"
        TERMINE = "TERMINE", "Terminé"
        ANNULE = "ANNULE", "Annulé"

    id_inventaire = models.AutoField(primary_key=True)

    code_inventaire = models.CharField(max_length=30, unique=True)

    entite_type = models.CharField(
        max_length=20,
        choices=EntiteType.choices
    )

    entite_id = models.PositiveIntegerField()

    type_inventaire = models.CharField(
        max_length=20,
        choices=TypeInventaire.choices,
        default=TypeInventaire.GENERAL
    )

    date_debut = models.DateField(default=timezone.localdate)
    date_fin = models.DateField(blank=True, null=True)

    statut = models.CharField(
        max_length=20,
        choices=StatutInventaire.choices,
        default=StatutInventaire.EN_COURS
    )

    effectue_par = models.ForeignKey(
        "comptes.Users",
        on_delete=models.SET_NULL,
        db_column="effectue_par",
        blank=True,
        null=True,
        related_name="inventaires_effectues"
    )

    cree_par = models.ForeignKey(
        "comptes.Users",
        on_delete=models.SET_NULL,
        db_column="cree_par",
        blank=True,
        null=True,
        related_name="inventaires_crees",
    )

    effectue_par_libre = models.CharField(max_length=500, blank=True, null=True)

    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "inventaire"

    def save(self, *args, **kwargs):
        if not self.code_inventaire:
            self.code_inventaire = generate_prefixed_code(Inventaire, "code_inventaire", "INV-")
        super().save(*args, **kwargs)

    def clean(self):
        if self.date_fin and self.date_fin < self.date_debut:
            raise ValidationError(
                "La date de fin ne peut pas être inférieure à la date de début."
            )

    def __str__(self):
        return self.code_inventaire


class InventaireDetail(models.Model):
    id_detail = models.AutoField(primary_key=True)

    id_inventaire = models.ForeignKey(
        "inventaires.Inventaire",
        on_delete=models.CASCADE,
        db_column="id_inventaire",
        related_name="details"
    )

    id_materiel = models.ForeignKey(
        "stock.Materiel",
        on_delete=models.PROTECT,
        db_column="id_materiel",
        blank=True,
        null=True,
        related_name="details_inventaire"
    )

    id_consommable = models.ForeignKey(
        "stock.Consommable",
        on_delete=models.PROTECT,
        db_column="id_consommable",
        blank=True,
        null=True,
        related_name="details_inventaire"
    )

    quantite_theorique = models.PositiveIntegerField(default=0)
    quantite_reelle = models.PositiveIntegerField(default=0)
    ecart = models.IntegerField(default=0)

    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "inventaire_detail"

    def clean(self):
        if not self.id_materiel and not self.id_consommable:
            raise ValidationError(
                "Le détail d'inventaire doit concerner soit un matériel, soit un consommable."
            )

        if self.id_materiel and self.id_consommable:
            raise ValidationError(
                "Le détail d'inventaire ne peut pas concerner un matériel et un consommable en même temps."
            )

    def save(self, *args, **kwargs):
        self.ecart = self.quantite_reelle - self.quantite_theorique
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Détail {self.id_detail} - {self.id_inventaire}"
