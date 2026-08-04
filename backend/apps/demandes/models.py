from django.db import models
from django.utils import timezone

from apps.core.code_generation import generate_prefixed_code


class Demande(models.Model):
    class OrigineType(models.TextChoices):
        DEPARTEMENT = "DEPARTEMENT", "Departement"
        DIRECTION = "DIRECTION", "Direction"
        MAGASIN = "MAGASIN", "Magasin"

    class TypeDemande(models.TextChoices):
        ACHAT = "ACHAT", "Achat"
        REAPPROVISIONNEMENT = "REAPPROVISIONNEMENT", "Reapprovisionnement"
        REPARATION = "REPARATION", "Reparation"
        AUTRE = "AUTRE", "Autre"

    class StatutDemande(models.TextChoices):
        EN_ATTENTE_DEPARTEMENT = "EN_ATTENTE_DEPARTEMENT", "En attente departement"
        EN_TRAITEMENT_MAGASIN = "EN_TRAITEMENT_MAGASIN", "En traitement magasin"
        TRAITEE = "TRAITEE", "Traitee"
        REJETEE = "REJETEE", "Rejetee"
        ANNULEE = "ANNULEE", "Annulee"

    id_demande = models.AutoField(primary_key=True)
    code_demande = models.CharField(max_length=30, unique=True)

    id_departement = models.ForeignKey(
        "organisation.Departement",
        on_delete=models.PROTECT,
        db_column="id_departement",
        related_name="demandes",
    )

    id_direction_demandeuse = models.ForeignKey(
        "organisation.Direction",
        on_delete=models.PROTECT,
        db_column="id_direction_demandeuse",
        related_name="demandes_emises",
        blank=True,
        null=True,
    )

    id_service_destinataire = models.ForeignKey(
        "organisation.Service",
        on_delete=models.PROTECT,
        db_column="id_service_destinataire",
        related_name="demandes_destinees",
        blank=True,
        null=True,
    )

    id_demandeur = models.ForeignKey(
        "comptes.Users",
        on_delete=models.PROTECT,
        db_column="id_demandeur",
        related_name="demandes",
    )

    origine_type = models.CharField(
        max_length=20,
        choices=OrigineType.choices,
        default=OrigineType.DIRECTION,
    )

    origine_id = models.PositiveIntegerField(blank=True, null=True)

    type_demande = models.CharField(
        max_length=30,
        choices=TypeDemande.choices,
    )

    id_materiel = models.ForeignKey(
        "stock.Materiel",
        on_delete=models.PROTECT,
        db_column="id_materiel",
        related_name="demandes",
        blank=True,
        null=True,
    )

    id_consommable = models.ForeignKey(
        "stock.Consommable",
        on_delete=models.PROTECT,
        db_column="id_consommable",
        related_name="demandes",
        blank=True,
        null=True,
    )

    quantite_demandee = models.PositiveIntegerField(default=1)

    statut = models.CharField(
        max_length=30,
        choices=StatutDemande.choices,
        default=StatutDemande.EN_ATTENTE_DEPARTEMENT,
    )

    date_demande = models.DateField(default=timezone.localdate)

    id_validateur_departement = models.ForeignKey(
        "comptes.Users",
        on_delete=models.SET_NULL,
        db_column="id_validateur_departement",
        related_name="demandes_validees_departement",
        blank=True,
        null=True,
    )
    date_validation_departement = models.DateTimeField(blank=True, null=True)

    id_magasinier_finalisateur = models.ForeignKey(
        "comptes.Users",
        on_delete=models.SET_NULL,
        db_column="id_magasinier_finalisateur",
        related_name="demandes_finalisees_magasin",
        blank=True,
        null=True,
    )
    date_finalisation = models.DateTimeField(blank=True, null=True)

    motif_rejet = models.CharField(max_length=500, blank=True, null=True)
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "demande"

    def save(self, *args, **kwargs):
        if not self.code_demande:
            self.code_demande = generate_prefixed_code(Demande, "code_demande", "DEM-")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.code_demande
