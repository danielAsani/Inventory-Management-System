from django.db import models


class MouvementStock(models.Model):
    id_mouvement = models.FloatField(primary_key=True)
    id_materiel = models.ForeignKey(
        'stock.Materiel',
        models.DO_NOTHING,
        db_column='id_materiel',
        blank=True,
        null=True,
    )
    id_consommable = models.ForeignKey(
        'stock.Consommable',
        models.DO_NOTHING,
        db_column='id_consommable',
        blank=True,
        null=True,
    )
    type_mouvement = models.CharField(max_length=20)
    quantite = models.FloatField()
    magasin_source_id = models.ForeignKey(
        'stock.Magasin',
        models.DO_NOTHING,
        db_column='magasin_source_id',
        related_name='+',
        blank=True,
        null=True,
    )
    magasin_destination_id = models.ForeignKey(
        'stock.Magasin',
        models.DO_NOTHING,
        db_column='magasin_destination_id',
        related_name='+',
        blank=True,
        null=True,
    )
    date_mouvement = models.DateField()
    fait_par = models.ForeignKey(
        'comptes.Users',
        models.DO_NOTHING,
        db_column='fait_par',
        blank=True,
        null=True,
    )
    reference_document = models.CharField(max_length=100, blank=True, null=True)
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'MOUVEMENT_STOCK'


class Affectation(models.Model):
    id_affectation = models.FloatField(primary_key=True)
    id_materiel = models.ForeignKey('stock.Materiel', models.DO_NOTHING, db_column='id_materiel')
    entite_type = models.CharField(max_length=20)
    entite_id = models.FloatField()
    date_affectation = models.DateField()
    date_retour = models.DateField(blank=True, null=True)
    statut = models.CharField(max_length=20)
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'AFFECTATION'


class Consommation(models.Model):
    id_consommation = models.FloatField(primary_key=True)
    id_consommable = models.ForeignKey('stock.Consommable', models.DO_NOTHING, db_column='id_consommable')
    quantite = models.FloatField()
    date_consommation = models.DateField()
    demandeur = models.CharField(max_length=100, blank=True, null=True)
    fait_par = models.ForeignKey(
        'comptes.Users',
        models.DO_NOTHING,
        db_column='fait_par',
        blank=True,
        null=True,
    )
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'CONSOMMATION'
