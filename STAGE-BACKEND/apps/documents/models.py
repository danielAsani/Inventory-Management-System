from django.db import models


class Document(models.Model):
    id_document = models.FloatField(primary_key=True)
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
    cree_par = models.ForeignKey('comptes.Users', models.DO_NOTHING, db_column='cree_par')
    type_document = models.CharField(max_length=100)
    numero_document = models.CharField(max_length=100, blank=True, null=True)
    titre = models.CharField(max_length=255)
    chemin_fichier = models.CharField(max_length=500, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    taille_fichier_octets = models.FloatField(blank=True, null=True)
    date_upload = models.DateField()
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DOCUMENT'
