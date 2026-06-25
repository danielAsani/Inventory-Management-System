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


class Direction(models.Model):
    id_direction = models.AutoField(primary_key=True)
    code_direction = models.CharField(max_length=20, unique=True)
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

    def __str__(self):
        return self.nom_direction


class Service(models.Model):
    id_service = models.AutoField(primary_key=True)
    code_service = models.CharField(max_length=20, unique=True)
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

    def __str__(self):
        return self.nom_service