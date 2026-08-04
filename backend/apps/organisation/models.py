from django.db import models


class Departement(models.Model):
    id_departement = models.AutoField(primary_key=True)
    code_departement = models.CharField(max_length=20, unique=True)
    nom_departement = models.CharField(max_length=100)
    abreviation = models.CharField(max_length=10, blank=True, null=True)
    statut = models.BooleanField(default=True)

    class Meta:
        db_table = "departement"

    def __str__(self):
        return self.nom_departement

    def save(self, *args, **kwargs):
        if self.code_departement:
            self.code_departement = self.code_departement.upper()
        if self.abreviation:
            self.abreviation = self.abreviation.upper()
        super().save(*args, **kwargs)


class Direction(models.Model):
    id_direction = models.AutoField(primary_key=True)
    code_direction = models.CharField(max_length=20)
    nom_direction = models.CharField(max_length=100)
    abreviation = models.CharField(max_length=10, blank=True, null=True)

    id_departement = models.ForeignKey(
        Departement,
        on_delete=models.PROTECT,
        db_column="id_departement",
        related_name="directions"
    )

    statut = models.BooleanField(default=True)

    class Meta:
        db_table = "direction"
        constraints = [
            models.UniqueConstraint(
                fields=["id_departement", "code_direction"],
                name="uniq_direction_code_par_departement",
            )
        ]

    def __str__(self):
        return self.nom_direction

    def save(self, *args, **kwargs):
        if self.code_direction:
            self.code_direction = self.code_direction.upper()
        if self.abreviation:
            self.abreviation = self.abreviation.upper()
        super().save(*args, **kwargs)


class Service(models.Model):
    id_service = models.AutoField(primary_key=True)
    code_service = models.CharField(max_length=20)
    nom_service = models.CharField(max_length=100)
    abreviation = models.CharField(max_length=10, blank=True, null=True)

    id_direction = models.ForeignKey(
        Direction,
        on_delete=models.PROTECT,
        db_column="id_direction",
        related_name="services"
    )

    statut = models.BooleanField(default=True)

    class Meta:
        db_table = "service"
        constraints = [
            models.UniqueConstraint(
                fields=["id_direction", "code_service"],
                name="uniq_service_code_par_direction",
            )
        ]

    def __str__(self):
        return self.nom_service

    def save(self, *args, **kwargs):
        if self.code_service:
            self.code_service = self.code_service.upper()
        if self.abreviation:
            self.abreviation = self.abreviation.upper()
        super().save(*args, **kwargs)
