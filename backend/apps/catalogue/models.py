from django.db import models
from django.utils import timezone


class Famille(models.Model):
    id_famille = models.AutoField(primary_key=True)
    code_famille = models.CharField(max_length=20, unique=True)
    nom_famille = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)
    statut = models.BooleanField(default=True)
    date_creation = models.DateField(default=timezone.localdate)

    class Meta:
        db_table = "famille"

    def __str__(self):
        return self.nom_famille


class Categorie(models.Model):
    id_categorie = models.AutoField(primary_key=True)
    code_categorie = models.CharField(max_length=20, unique=True)
    nom_categorie = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)

    id_famille = models.ForeignKey(
        Famille,
        on_delete=models.PROTECT,
        db_column="id_famille",
        related_name="categories"
    )

    statut = models.BooleanField(default=True)
    date_creation = models.DateField(default=timezone.localdate)

    class Meta:
        db_table = "categorie"

    def __str__(self):
        return self.nom_categorie


class UniteMesure(models.Model):
    id_unite = models.AutoField(primary_key=True)
    code_unite = models.CharField(max_length=10, unique=True)
    nom_unite = models.CharField(max_length=30)
    symbole = models.CharField(max_length=10)

    class Meta:
        db_table = "unite_mesure"

    def __str__(self):
        return self.symbole


class Fournisseur(models.Model):
    id_fournisseur = models.AutoField(primary_key=True)
    nom_fournisseur = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)

    rccm = models.CharField(max_length=50, unique=True, blank=True, null=True)
    nif = models.CharField(max_length=30, unique=True, blank=True, null=True)

    date_creation = models.DateField(default=timezone.localdate)
    statut = models.BooleanField(default=True)

    class Meta:
        db_table = "fournisseur"

    def __str__(self):
        return self.nom_fournisseur