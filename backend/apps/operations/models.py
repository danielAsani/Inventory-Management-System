from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


TRACEABILITY_TYPE_PREFIXES = {
    "DEPARTEMENT": "DEP",
    "DIRECTION": "DIR",
    "AGENT": "AGT",
}


def normalize_traceability_token(value):
    return "".join(character for character in str(value or "").upper() if character.isalnum() or character == "-")


class MouvementStock(models.Model):
    class TypeMouvement(models.TextChoices):
        ENTREE = "ENTREE", "EntrÃ©e"
        SORTIE = "SORTIE", "Sortie"
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

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.type_mouvement} - {self.date_mouvement}"
    

class Affectation(models.Model):
    class EntiteType(models.TextChoices):
        DEPARTEMENT = "DEPARTEMENT", "Departement"
        DIRECTION = "DIRECTION", "Direction"
        AGENT = "AGENT", "Agent"

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

    entite_id = models.PositiveIntegerField(blank=True, null=True)

    agent_id_departement = models.ForeignKey(
        "organisation.Departement",
        on_delete=models.SET_NULL,
        db_column="agent_id_departement",
        blank=True,
        null=True,
        related_name="affectations_agents",
    )

    agent_id_direction = models.ForeignKey(
        "organisation.Direction",
        on_delete=models.SET_NULL,
        db_column="agent_id_direction",
        blank=True,
        null=True,
        related_name="affectations_agents",
    )

    agent_id_service = models.ForeignKey(
        "organisation.Service",
        on_delete=models.SET_NULL,
        db_column="agent_id_service",
        blank=True,
        null=True,
        related_name="affectations_agents",
    )

    agent_matricule = models.CharField(max_length=30, blank=True, null=True)
    agent_nom_complet = models.CharField(max_length=150, blank=True, null=True)
    agent_telephone = models.CharField(max_length=20, blank=True, null=True)

    date_affectation = models.DateField(default=timezone.localdate)
    date_retour = models.DateField(blank=True, null=True)

    code_affectation = models.CharField(max_length=80, unique=True, blank=True, null=True)
    code_barre = models.CharField(max_length=80, unique=True, blank=True, null=True)
    qr_code = models.CharField(max_length=190, unique=True, blank=True, null=True)

    statut = models.CharField(
        max_length=20,
        choices=StatutAffectation.choices,
        default=StatutAffectation.ACTIVE
    )

    observation = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = "affectation"

    def _traceability_values(self, suffix=None):
        materiel_code = normalize_traceability_token(getattr(self.id_materiel, "code_materiel", None))
        entite_prefix = TRACEABILITY_TYPE_PREFIXES.get(
            self.entite_type,
            normalize_traceability_token(self.entite_type)[:3],
        )
        date_value = self.date_affectation or timezone.localdate()
        entite_token = self.entite_id
        if self.entite_type == self.EntiteType.AGENT:
            entite_token = normalize_traceability_token(self.agent_matricule)
        base = f"AFF-{materiel_code}-{entite_prefix}{entite_token}-{date_value:%Y%m%d}"
        if suffix:
            base = f"{base}-{suffix:02d}"
        return {
            "code_affectation": base,
            "code_barre": base,
            "qr_code": f"AFF|{base}|MAT:{materiel_code}|TO:{self.entite_type}:{entite_token}|DATE:{date_value:%Y-%m-%d}",
        }

    def refresh_traceability(self):
        suffix = None
        while True:
            values = self._traceability_values(suffix)
            conflicts = Affectation.objects.filter(
                models.Q(code_affectation=values["code_affectation"])
                | models.Q(code_barre=values["code_barre"])
                | models.Q(qr_code=values["qr_code"])
            )
            if self.pk:
                conflicts = conflicts.exclude(pk=self.pk)
            if not conflicts.exists():
                self.code_affectation = values["code_affectation"]
                self.code_barre = values["code_barre"]
                self.qr_code = values["qr_code"]
                return
            suffix = 1 if suffix is None else suffix + 1

    def save(self, *args, **kwargs):
        has_destination = self.entite_id or (self.entite_type == self.EntiteType.AGENT and self.agent_matricule)
        if self.id_materiel_id and self.entite_type and has_destination and self.date_affectation:
            self.refresh_traceability()
            if kwargs.get("update_fields"):
                kwargs["update_fields"] = set(kwargs["update_fields"]).union(
                    {"code_affectation", "code_barre", "qr_code"}
                )
        super().save(*args, **kwargs)

    def clean(self):
        if self.date_retour and self.date_retour < self.date_affectation:
            raise ValidationError(
                "La date de retour ne peut pas Ãªtre infÃ©rieure Ã  la date d'affectation."
            )

    def __str__(self):
        return f"Affectation {self.id_affectation} - {self.id_materiel}"
    


class Consommation(models.Model):
    class DestinationType(models.TextChoices):
        DEPARTEMENT = "DEPARTEMENT", "Departement"
        DIRECTION = "DIRECTION", "Direction"

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

    destination_type = models.CharField(
        max_length=20,
        choices=DestinationType.choices,
        default=DestinationType.DEPARTEMENT,
    )

    id_departement = models.ForeignKey(
        "organisation.Departement",
        on_delete=models.PROTECT,
        db_column="id_departement",
        blank=True,
        null=True,
        related_name="consommations",
    )

    id_direction = models.ForeignKey(
        "organisation.Direction",
        on_delete=models.PROTECT,
        db_column="id_direction",
        blank=True,
        null=True,
        related_name="consommations",
    )

    id_service = models.ForeignKey(
        "organisation.Service",
        on_delete=models.PROTECT,
        db_column="id_service",
        blank=True,
        null=True,
        related_name="consommations",
    )

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
