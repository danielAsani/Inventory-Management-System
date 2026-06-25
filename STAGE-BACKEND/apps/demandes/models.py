from django.db import models
from django.utils import timezone


class Demande(models.Model):
    class OrigineType(models.TextChoices):
        DEPARTEMENT = "DEPARTEMENT", "Département"
        DIRECTION = "DIRECTION", "Direction"
        SERVICE = "SERVICE", "Service"
        MAGASIN = "MAGASIN", "Magasin"

    class TypeDemande(models.TextChoices):
        ACHAT = "ACHAT", "Achat"
        REAPPROVISIONNEMENT = "REAPPROVISIONNEMENT", "Réapprovisionnement"
        REPARATION = "REPARATION", "Réparation"
        AUTRE = "AUTRE", "AUTRE",

    class StatutDemande(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        VALIDEE = "VALIDEE", "Validée"
        REJETEE = "REJETEE", "Rejetée"
        TRAITEE = "TRAITEE", "Traitée"
        ANNULEE = "ANNULEE", "Annulée"

    id_demande = models.AutoField(primary_key=True)

    code_demande = models.CharField(max_length=30, unique=True)

    id_departement = models.ForeignKey(
        "organisation.Departement",
        on_delete=models.PROTECT,
        db_column="id_departement",
        related_name="demandes"
    )

    id_demandeur = models.ForeignKey(
        "comptes.Users",
        on_delete=models.PROTECT,
        db_column="id_demandeur",
        related_name="demandes"
    )

    origine_type = models.CharField(
        max_length=20,
        choices=OrigineType.choices,
        default=OrigineType.DEPARTEMENT
    )

    origine_id = models.PositiveIntegerField(blank=True, null=True)

    type_demande = models.CharField(
        max_length=30,
        choices=TypeDemande.choices
    )

    statut = models.CharField(
        max_length=20,
        choices=StatutDemande.choices,
        default=StatutDemande.EN_ATTENTE
    )

    date_demande = models.DateField(default=timezone.localdate)

    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "demande"

    def __str__(self):
        return self.code_demande