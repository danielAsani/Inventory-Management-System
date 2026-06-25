# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Famille(models.Model):
    id_famille = models.FloatField(primary_key=True)
    code_famille = models.CharField(unique=True, max_length=20)
    nom_famille = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)
    statut = models.BooleanField(default=True)
    date_creation = models.DateField()

    class Meta:
        managed = False
        db_table = 'FAMILLE'


class Categorie(models.Model):
    id_categorie = models.FloatField(primary_key=True)
    code_categorie = models.CharField(unique=True, max_length=20)
    nom_categorie = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)
    id_famille = models.ForeignKey(Famille, models.DO_NOTHING, db_column='id_famille')
    statut = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'CATEGORIE'


class UniteMesure(models.Model):
    id_unite = models.FloatField(primary_key=True)
    code_unite = models.CharField(unique=True, max_length=10)
    nom_unite = models.CharField(max_length=30)
    symbole = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'UNITE_MESURE'


class Fournisseur(models.Model):
    id_fournisseur = models.FloatField(primary_key=True)
    nom_fournisseur = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    rccm = models.CharField(unique=True, max_length=50, blank=True, null=True)
    nif = models.CharField(unique=True, max_length=30, blank=True, null=True)
    date_creation = models.DateField()

    class Meta:
        managed = False
        db_table = 'FOURNISSEUR'
