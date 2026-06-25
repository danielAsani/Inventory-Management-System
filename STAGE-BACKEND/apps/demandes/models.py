from django.db import models


class Demande(models.Model):
    id_demande = models.FloatField(primary_key=True)
    code_demande = models.CharField(max_length=30)
    id_departement = models.ForeignKey(
        'organisation.Departement',
        models.DO_NOTHING,
        db_column='id_departement',
    )
    id_demandeur = models.ForeignKey('comptes.Users', models.DO_NOTHING, db_column='id_demandeur')
    origine_type = models.CharField(max_length=20)
    origine_id = models.FloatField(blank=True, null=True)
    type_demande = models.CharField(max_length=20)
    statut = models.CharField(max_length=20)
    date_demande = models.DateField()
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DEMANDE'
