# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Departement(models.Model):
    id_departement = models.FloatField(primary_key=True)
    code_departement = models.CharField(unique=True, max_length=20)
    nom_departement = models.CharField(max_length=100)
    abreviation = models.CharField(max_length=10)
    statut = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'DEPARTEMENT'


class Direction(models.Model):
    id_direction = models.FloatField(primary_key=True)
    code_direction = models.CharField(unique=True, max_length=20)
    nom_direction = models.CharField(max_length=100)
    abreviation = models.CharField(max_length=10)
    id_departement = models.ForeignKey(Departement, models.DO_NOTHING, db_column='id_departement')
    statut = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'DIRECTION'


class Service(models.Model):
    id_service = models.FloatField(primary_key=True)
    code_service = models.CharField(unique=True, max_length=20)
    nom_service = models.CharField(max_length=100)
    abreviation = models.CharField(max_length=10)
    id_direction = models.ForeignKey(Direction, models.DO_NOTHING, db_column='id_direction')
    statut = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'SERVICE'
