
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Role(models.Model):
    id_role = models.AutoField(primary_key=True)
    code_role = models.CharField(max_length=30, unique=True)
    nom_role = models.CharField(max_length=30)
    description = models.CharField(max_length=255, blank=True, null=True)
    statut = models.BooleanField(default=True)

    class Meta:
        db_table = "role"

    def __str__(self):
        return self.nom_role



class Users(models.Model):
    class ScopeType(models.TextChoices):
        GENERAL = "GENERAL", "Général"
        DEPARTEMENT = "DEPARTEMENT", "Département"
        DIRECTION = "DIRECTION", "Direction"
        SERVICE = "SERVICE", "Service"
        MAGASIN = "MAGASIN", "Magasin"

    id_users = models.AutoField(primary_key=True)

    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    nom_users = models.CharField(max_length=100)
    matricule = models.CharField(max_length=30, unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    password_hash = models.CharField(max_length=255)

    statut = models.BooleanField(default=True)
    dernier_login = models.DateTimeField(blank=True, null=True)
    date_ajout = models.DateField(default=timezone.localdate)

    id_role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        db_column="id_role",
        related_name="users"
    )

    scope_type = models.CharField(
        max_length=20,
        choices=ScopeType.choices,
        default=ScopeType.GENERAL
    )

    id_departement = models.ForeignKey(
        "organisation.Departement",
        on_delete=models.SET_NULL,
        db_column="id_departement",
        blank=True,
        null=True,
        related_name="users"
    )

    id_direction = models.ForeignKey(
        "organisation.Direction",
        on_delete=models.SET_NULL,
        db_column="id_direction",
        blank=True,
        null=True,
        related_name="users"
    )

    id_service = models.ForeignKey(
        "organisation.Service",
        on_delete=models.SET_NULL,
        db_column="id_service",
        blank=True,
        null=True,
        related_name="users"
    )

    id_magasin = models.ForeignKey(
        "stock.Magasin",
        on_delete=models.SET_NULL,
        db_column="id_magasin",
        blank=True,
        null=True,
        related_name="users"
    )

    class Meta:
        db_table = "users"

    def clean(self):
        errors = {}

        if self.scope_type == self.ScopeType.DEPARTEMENT and not self.id_departement:
            errors["id_departement"] = "Le département est obligatoire pour un scope DEPARTEMENT."

        if self.scope_type == self.ScopeType.DIRECTION and not self.id_direction:
            errors["id_direction"] = "La direction est obligatoire pour un scope DIRECTION."

        if self.scope_type == self.ScopeType.SERVICE and not self.id_service:
            errors["id_service"] = "Le service est obligatoire pour un scope SERVICE."

        if self.scope_type == self.ScopeType.MAGASIN and not self.id_magasin:
            errors["id_magasin"] = "Le magasin est obligatoire pour un scope MAGASIN."

        if self.scope_type == self.ScopeType.GENERAL:
            if self.id_departement or self.id_direction or self.id_service or self.id_magasin:
                errors["scope_type"] = "Un utilisateur GENERAL ne doit pas avoir de périmètre précis."

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.nom_users} - {self.matricule}"


