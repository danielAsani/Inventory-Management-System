from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Magasin(models.Model):
    id_magasin = models.AutoField(primary_key=True)

    code_magasin = models.CharField(max_length=20, unique=True)
    nom_magasin = models.CharField(max_length=100)

    id_service = models.ForeignKey(
        "organisation.Service",
        on_delete=models.SET_NULL,
        db_column="id_service",
        blank=True,
        null=True,
        related_name="magasins"
    )

    description_localisation = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    date_creation = models.DateField(default=timezone.localdate)
    statut = models.BooleanField(default=True)

    class Meta:
        db_table = "magasin"

    def __str__(self):
        return self.nom_magasin


class Materiel(models.Model):
    class EtatMateriel(models.TextChoices):
        NEUF = "NEUF", "Neuf"
        BON = "BON", "Bon état"
        EN_STOCK = "EN_STOCK", "En stock"
        AFFECTE = "AFFECTE", "Affecté"
        EN_PANNE = "EN_PANNE", "En panne"
        EN_REPARATION = "EN_REPARATION", "En réparation"
        HORS_SERVICE = "HORS_SERVICE", "Hors service"

    id_materiel = models.AutoField(primary_key=True)

    code_materiel = models.CharField(max_length=25, unique=True)

    id_categorie = models.ForeignKey(
        "catalogue.Categorie",
        on_delete=models.PROTECT,
        db_column="id_categorie",
        related_name="materiels"
    )

    id_magasin = models.ForeignKey(
        Magasin,
        on_delete=models.SET_NULL,
        db_column="id_magasin",
        blank=True,
        null=True,
        related_name="materiels"
    )

    id_fournisseur = models.ForeignKey(
        "catalogue.Fournisseur",
        on_delete=models.SET_NULL,
        db_column="id_fournisseur",
        blank=True,
        null=True,
        related_name="materiels"
    )

    numero_serie = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=150, blank=True, null=True)

    date_achat = models.DateField()
    date_mise_en_service = models.DateField(blank=True, null=True)

    prix_achat = models.DecimalField(max_digits=13, decimal_places=2)
    devise = models.CharField(max_length=10, default="USD")

    duree_garantie_mois = models.PositiveIntegerField(default=0)
    garantie_fin = models.DateField(blank=True, null=True)

    etat = models.CharField(
        max_length=20,
        choices=EtatMateriel.choices,
        default=EtatMateriel.NEUF
    )

    code_barre = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    qr_code = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

    date_enregistrement = models.DateField(default=timezone.localdate)

    observation = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    class Meta:
        db_table = "materiel"

    def clean(self):
        errors = {}

        if self.date_mise_en_service and self.date_mise_en_service < self.date_achat:
            errors["date_mise_en_service"] = (
                "La date de mise en service ne peut pas être avant la date d'achat."
            )

        if self.garantie_fin and self.garantie_fin < self.date_achat:
            errors["garantie_fin"] = (
                "La date de fin de garantie ne peut pas être avant la date d'achat."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        modele = self.modele or ""
        return f"{self.code_materiel} - {self.marque} {modele}"


class Consommable(models.Model):
    id_consommable = models.AutoField(primary_key=True)

    code_consommable = models.CharField(max_length=25, unique=True)
    nom_consommable = models.CharField(max_length=100)

    id_categorie = models.ForeignKey(
        "catalogue.Categorie",
        on_delete=models.PROTECT,
        db_column="id_categorie",
        related_name="consommables"
    )

    id_unite = models.ForeignKey(
        "catalogue.UniteMesure",
        on_delete=models.PROTECT,
        db_column="id_unite",
        related_name="consommables"
    )

    id_magasin = models.ForeignKey(
        Magasin,
        on_delete=models.SET_NULL,
        db_column="id_magasin",
        blank=True,
        null=True,
        related_name="consommables"
    )

    quantite_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    seuil_alerte = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    date_creation = models.DateField(default=timezone.localdate)
    statut = models.BooleanField(default=True)

    class Meta:
        db_table = "consommable"

    def clean(self):
        errors = {}

        if self.quantite_stock < 0:
            errors["quantite_stock"] = (
                "La quantité en stock ne peut pas être négative."
            )

        if self.seuil_alerte is not None and self.seuil_alerte < 0:
            errors["seuil_alerte"] = (
                "Le seuil d'alerte ne peut pas être négatif."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.nom_consommable