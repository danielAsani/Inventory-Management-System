from django.db import models


class Entretien(models.Model):
    id_entretien = models.FloatField(primary_key=True)
    id_materiel = models.ForeignKey('stock.Materiel', models.DO_NOTHING, db_column='id_materiel')
    date_entretien = models.DateField()
    date_fin_prevue = models.DateField(blank=True, null=True)
    date_fin_reelle = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    cout_entretien = models.DecimalField(max_digits=12, decimal_places=2)
    type_entretien = models.CharField(max_length=20)
    kilometrage = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    type_prestataire = models.CharField(max_length=20)
    nom_prestataire = models.CharField(max_length=100, blank=True, null=True)
    garantie_entretien_mois = models.IntegerField(blank=True, null=True)
    prochaine_date = models.DateField(blank=True, null=True)
    statut = models.CharField(max_length=20)
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ENTRETIEN'


class Reparation(models.Model):
    id_reparation = models.FloatField(primary_key=True)
    id_materiel = models.ForeignKey('stock.Materiel', models.DO_NOTHING, db_column='id_materiel')
    date_reparation = models.DateField()
    date_fin_prevue = models.DateField(blank=True, null=True)
    date_fin_reelle = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    cout_reparation = models.DecimalField(max_digits=12, decimal_places=2)
    type_prestataire = models.CharField(max_length=20)
    nom_prestataire = models.CharField(max_length=100, blank=True, null=True)
    garantie_reparation_mois = models.IntegerField(blank=True, null=True)
    statut = models.CharField(max_length=20)
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'REPARATION'
