from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class MouvementStock(models.Model):
    class TypeMouvement(models.TextChoices):
        ENTREE = "ENTREE", "EntrÃ©e"
        SORTIE = "SORTIE", "Sortie"
        TRANSFERT = "TRANSFERT", "Transfert"
        AJUSTEMENT = "AJUSTEMENT", "Ajustement"

    id_mouvement = models.AutoField(primary_key=True)

    id_materiel = models.ForeignKey(
        "stock.Materiel",
        on_delete=models.PROTECT,
        db_column="id_materiel",
        blank=True,
        null=True,
        related_name="mouvements_stock"
    )

    id_consommable = models.ForeignKey(
        "stock.Consommable",
        on_delete=models.PROTECT,
        db_column="id_consommable",
        blank=True,
        null=True,
        related_name="mouvements_stock"
    )

    type_mouvement = models.CharField(
        max_length=20,
        choices=TypeMouvement.choices
    )

    quantite = models.PositiveIntegerField(default=1)

    magasin_source = models.ForeignKey(
        "stock.Magasin",
        on_delete=models.PROTECT,
        db_column="magasin_source_id",
        related_name="mouvements_sortants",
        blank=True,
        null=True
    )

    magasin_destination = models.ForeignKey(
        "stock.Magasin",
        on_delete=models.PROTECT,
        db_column="magasin_destination_id",
        related_name="mouvements_entrants",
        blank=True,
        null=True
    )

    date_mouvement = models.DateField(default=timezone.localdate)

    fait_par = models.ForeignKey(
        "comptes.Users",
        on_delete=models.SET_NULL,
        db_column="fait_par",
        blank=True,
        null=True,
        related_name="mouvements_effectues"
    )

    reference_document = models.CharField(max_length=100, blank=True, null=True)
    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "mouvement_stock"

    def clean(self):
        errors = {}

        if not self.id_materiel and not self.id_consommable:
            errors["id_materiel"] = "Le mouvement doit concerner soit un matÃ©riel, soit un consommable."

        if self.id_materiel and self.id_consommable:
            errors["id_materiel"] = "Le mouvement ne peut pas concerner un matÃ©riel et un consommable en mÃªme temps."

        if self.type_mouvement == self.TypeMouvement.ENTREE:
            if not self.magasin_destination:
                errors["magasin_destination"] = "Une entrÃ©e doit avoir un magasin de destination."

        if self.type_mouvement == self.TypeMouvement.SORTIE:
            if not self.magasin_source:
                errors["magasin_source"] = "Une sortie doit avoir un magasin source."

        if self.type_mouvement == self.TypeMouvement.TRANSFERT:
            if not self.magasin_source:
                errors["magasin_source"] = "Un transfert doit avoir un magasin source."

            if not self.magasin_destination:
                errors["magasin_destination"] = "Un transfert doit avoir un magasin de destination."

            if self.magasin_source and self.magasin_destination:
                if self.magasin_source == self.magasin_destination:
                    errors["magasin_destination"] = "Le magasin source et le magasin destination doivent Ãªtre diffÃ©rents."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.type_mouvement} - {self.date_mouvement}"
    

class Affectation(models.Model):
    class EntiteType(models.TextChoices):
        DEPARTEMENT = "DEPARTEMENT", "DÃ©partement"
        DIRECTION = "DIRECTION", "Direction"
        SERVICE = "SERVICE", "Service"
        UTILISATEUR = "UTILISATEUR", "Utilisateur"

    class StatutAffectation(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        RETOURNEE = "RETOURNEE", "RetournÃ©e"
        ANNULEE = "ANNULEE", "AnnulÃ©e"

    id_affectation = models.AutoField(primary_key=True)

    id_materiel = models.ForeignKey(
        "stock.Materiel",
        on_delete=models.PROTECT,
        db_column="id_materiel",
        related_name="affectations"
    )

    entite_type = models.CharField(
        max_length=20,
        choices=EntiteType.choices
    )

    entite_id = models.PositiveIntegerField()

    date_affectation = models.DateField(default=timezone.localdate)
    date_retour = models.DateField(blank=True, null=True)

    statut = models.CharField(
        max_length=20,
        choices=StatutAffectation.choices,
        default=StatutAffectation.ACTIVE
    )

    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "affectation"

    def clean(self):
        if self.date_retour and self.date_retour < self.date_affectation:
            raise ValidationError(
                "La date de retour ne peut pas Ãªtre infÃ©rieure Ã  la date d'affectation."
            )

    def __str__(self):
        return f"Affectation {self.id_affectation} - {self.id_materiel}"
    


class Consommation(models.Model):
    id_consommation = models.AutoField(primary_key=True)

    id_consommable = models.ForeignKey(
        "stock.Consommable",
        on_delete=models.PROTECT,
        db_column="id_consommable",
        related_name="consommations"
    )

    quantite = models.PositiveIntegerField()

    date_consommation = models.DateField(default=timezone.localdate)

    demandeur = models.CharField(max_length=100, blank=True, null=True)

    fait_par = models.ForeignKey(
        "comptes.Users",
        on_delete=models.SET_NULL,
        db_column="fait_par",
        blank=True,
        null=True,
        related_name="consommations_effectuees"
    )

    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "consommation"

    def __str__(self):
        return f"Consommation {self.id_consommation} - {self.id_consommable}"
