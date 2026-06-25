# This is an auto-generated Django model module.
# Models generated from existing Oracle tables.
# Important: managed = False means Django will not create or modify these tables.

from django.db import models


class Magasin(models.Model):
    id_magasin = models.FloatField(primary_key=True)
    code_magasin = models.CharField(unique=True, max_length=20)
    nom_magasin = models.CharField(max_length=100)

    # Relation vers l'app organisation
    id_service = models.ForeignKey(
        'organisation.Service',
        models.DO_NOTHING,
        db_column='id_service',
        blank=True,
        null=True
    )

    description_localisation = models.CharField(max_length=500, blank=True, null=True)
    date_creation = models.DateField()
    statut = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'MAGASIN'


class Materiel(models.Model):
    id_materiel = models.FloatField(primary_key=True)
    code_materiel = models.CharField(unique=True, max_length=25)

    # Relation vers l'app catalogue
    id_categorie = models.ForeignKey(
        'catalogue.Categorie',
        models.DO_NOTHING,
        db_column='id_categorie'
    )

    # Relation vers la table Magasin dans la même app stock
    id_magasin = models.ForeignKey(
        Magasin,
        models.DO_NOTHING,
        db_column='id_magasin',
    )

    # Relation vers l'app catalogue
    id_fournisseur = models.ForeignKey(
        'catalogue.Fournisseur',
        models.DO_NOTHING,
        db_column='id_fournisseur',
    )

    numero_serie = models.CharField(unique=True, max_length=50, blank=True, null=True)
    marque = models.CharField(max_length=100, )
    modele = models.CharField(max_length=150, )
    date_achat = models.DateField()
    date_mise_en_service = models.DateField(blank=True, null=True)
    prix_achat = models.DecimalField(max_digits=13, decimal_places=2, )
    devise = models.CharField(max_length=10, default="USD")
    duree_garantie_mois = models.IntegerField()
    garantie_fin = models.DateField()
    etat = models.CharField(max_length=20, default="Neuve")
    code_barre = models.CharField(unique=True, max_length=50, )
    qr_code = models.CharField(unique=True, max_length=100)
    date_enregistrement = models.DateField()
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'MATERIEL'


class Consommable(models.Model):
    id_consommable = models.FloatField(primary_key=True)
    code_consommable = models.CharField(unique=True, max_length=25)
    nom_consommable = models.CharField(max_length=100)

    # Relation vers l'app catalogue
    id_categorie = models.ForeignKey(
        'catalogue.Categorie',
        models.DO_NOTHING,
        db_column='id_categorie'
    )

    # Relation vers l'app catalogue
    id_unite = models.ForeignKey(
        'catalogue.UniteMesure',
        models.DO_NOTHING,
        db_column='id_unite'
    )

    # Relation vers la table Magasin dans la même app stock
    id_magasin = models.ForeignKey(
        Magasin,
        models.DO_NOTHING,
        db_column='id_magasin', 
        blank= True, 
        null= True,
    )

    quantite_stock = models.FloatField()
    seuil_alerte = models.FloatField(blank=True, null= True)
    date_creation = models.DateField()
    statut = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'CONSOMMABLE'