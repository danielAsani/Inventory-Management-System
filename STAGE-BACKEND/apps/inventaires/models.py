from django.db import models


class Inventaire(models.Model):
    id_inventaire = models.FloatField(primary_key=True)
    code_inventaire = models.CharField(max_length=30)
    entite_type = models.CharField(max_length=20)
    entite_id = models.FloatField()
    type_inventaire = models.CharField(max_length=20)
    date_debut = models.DateField()
    date_fin = models.DateField(blank=True, null=True)
    statut = models.CharField(max_length=20)
    effectue_par = models.ForeignKey(
        'comptes.Users',
        models.DO_NOTHING,
        db_column='effectue_par',
        blank=True,
        null=True,
    )
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'INVENTAIRE'


class InventaireDetail(models.Model):
    id_detail = models.FloatField(primary_key=True)
    id_inventaire = models.ForeignKey(
        'inventaires.Inventaire',
        models.DO_NOTHING,
        db_column='id_inventaire',
    )
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
    quantite_theorique = models.FloatField()
    quantite_reelle = models.FloatField()
    ecart = models.FloatField(blank=True, null=True)
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'INVENTAIRE_DETAIL'
