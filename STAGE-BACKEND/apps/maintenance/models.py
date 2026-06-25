from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Entretien(models.Model):
    class TypeEntretien(models.TextChoices):
        PREVENTIF = "PREVENTIF", "Préventif"
        CORRECTIF = "CORRECTIF", "Correctif"
        CONTROLE = "CONTROLE", "Contrôle"

    class TypePrestataire(models.TextChoices):
        AUCUN = "AUCUN", "Aucun"
        INTERNE = "INTERNE", "Interne"
        PRESTATAIRE = "PRESTATAIRE", "Prestataire"
        CONSTRUCTEUR = "CONSTRUCTEUR", "Constructeur"

    class StatutEntretien(models.TextChoices):
        PLANIFIE = "PLANIFIE", "Planifié"
        EN_COURS = "EN_COURS", "En cours"
        TERMINE = "TERMINE", "Terminé"
        ANNULE = "ANNULE", "Annulé"

    id_entretien = models.AutoField(primary_key=True)

    id_materiel = models.ForeignKey(
        "stock.Materiel",
        on_delete=models.PROTECT,
        db_column="id_materiel",
        related_name="entretiens"
    )

    date_entretien = models.DateField(default=timezone.localdate)
    date_fin_prevue = models.DateField(blank=True, null=True)
    date_fin_reelle = models.DateField(blank=True, null=True)

    description = models.CharField(max_length=500, blank=True, null=True)

    cout_entretien = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    type_entretien = models.CharField(
        max_length=20,
        choices=TypeEntretien.choices,
        default=TypeEntretien.PREVENTIF
    )

    kilometrage = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True
    )

    type_prestataire = models.CharField(
        max_length=20,
        choices=TypePrestataire.choices,
        default=TypePrestataire.AUCUN
    )

    nom_prestataire = models.CharField(max_length=100, blank=True, null=True)

    garantie_entretien_mois = models.PositiveIntegerField(blank=True, null=True)

    prochaine_date = models.DateField(blank=True, null=True)

    statut = models.CharField(
        max_length=20,
        choices=StatutEntretien.choices,
        default=StatutEntretien.PLANIFIE
    )

    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "entretien"

    def clean(self):
        errors = {}

        if self.date_fin_prevue and self.date_fin_prevue < self.date_entretien:
            errors["date_fin_prevue"] = (
                "La date de fin prévue ne peut pas être avant la date d'entretien."
            )

        if self.date_fin_reelle and self.date_fin_reelle < self.date_entretien:
            errors["date_fin_reelle"] = (
                "La date de fin réelle ne peut pas être avant la date d'entretien."
            )

        if self.prochaine_date and self.prochaine_date < self.date_entretien:
            errors["prochaine_date"] = (
                "La prochaine date d'entretien ne peut pas être avant la date actuelle d'entretien."
            )

        if self.cout_entretien < 0:
            errors["cout_entretien"] = "Le coût d'entretien ne peut pas être négatif."

        if self.kilometrage is not None and self.kilometrage < 0:
            errors["kilometrage"] = "Le kilométrage ne peut pas être négatif."

        if self.garantie_entretien_mois is not None and self.garantie_entretien_mois < 0:
            errors["garantie_entretien_mois"] = (
                "La garantie d'entretien ne peut pas être négative."
            )

        if self.type_prestataire in [
            self.TypePrestataire.PRESTATAIRE,
            self.TypePrestataire.CONSTRUCTEUR,
        ] and not self.nom_prestataire:
            errors["nom_prestataire"] = (
                "Le nom du prestataire est obligatoire pour ce type de prestataire."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Entretien {self.id_entretien} - {self.id_materiel}"


class Reparation(models.Model):
    class TypePrestataire(models.TextChoices):
        AUCUN = "AUCUN", "Aucun"
        INTERNE = "INTERNE", "Interne"
        PRESTATAIRE = "PRESTATAIRE", "Prestataire"
        CONSTRUCTEUR = "CONSTRUCTEUR", "Constructeur"

    class StatutReparation(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        EN_COURS = "EN_COURS", "En cours"
        TERMINEE = "TERMINEE", "Terminée"
        ANNULEE = "ANNULEE", "Annulée"

    id_reparation = models.AutoField(primary_key=True)

    id_materiel = models.ForeignKey(
        "stock.Materiel",
        on_delete=models.PROTECT,
        db_column="id_materiel",
        related_name="reparations"
    )

    date_reparation = models.DateField(default=timezone.localdate)
    date_fin_prevue = models.DateField(blank=True, null=True)
    date_fin_reelle = models.DateField(blank=True, null=True)

    description = models.CharField(max_length=500, blank=True, null=True)

    cout_reparation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    type_prestataire = models.CharField(
        max_length=20,
        choices=TypePrestataire.choices,
        default=TypePrestataire.AUCUN
    )

    nom_prestataire = models.CharField(max_length=100, blank=True, null=True)

    garantie_reparation_mois = models.PositiveIntegerField(blank=True, null=True)

    statut = models.CharField(
        max_length=20,
        choices=StatutReparation.choices,
        default=StatutReparation.EN_ATTENTE
    )

    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "reparation"

    def clean(self):
        errors = {}

        if self.date_fin_prevue and self.date_fin_prevue < self.date_reparation:
            errors["date_fin_prevue"] = (
                "La date de fin prévue ne peut pas être avant la date de réparation."
            )

        if self.date_fin_reelle and self.date_fin_reelle < self.date_reparation:
            errors["date_fin_reelle"] = (
                "La date de fin réelle ne peut pas être avant la date de réparation."
            )

        if self.cout_reparation < 0:
            errors["cout_reparation"] = "Le coût de réparation ne peut pas être négatif."

        if self.garantie_reparation_mois is not None and self.garantie_reparation_mois < 0:
            errors["garantie_reparation_mois"] = (
                "La garantie de réparation ne peut pas être négative."
            )

        if self.type_prestataire in [
            self.TypePrestataire.PRESTATAIRE,
            self.TypePrestataire.CONSTRUCTEUR,
        ] and not self.nom_prestataire:
            errors["nom_prestataire"] = (
                "Le nom du prestataire est obligatoire pour ce type de prestataire."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Réparation {self.id_reparation} - {self.id_materiel}"