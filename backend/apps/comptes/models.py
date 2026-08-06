from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


class Role(models.Model):
    class RoleCode(models.TextChoices):
        ADMIN = "ADMIN", "Administrateur"
        GESTION = "GESTION", "Gestion"
        MAGASIN = "MAGASIN", "Magasin"

    id_role = models.AutoField(primary_key=True)
    code_role = models.CharField(max_length=20, choices=RoleCode.choices, unique=True)
    nom_role = models.CharField(max_length=30)
    description = models.CharField(max_length=255, blank=True, null=True)
    statut = models.BooleanField(default=True)

    class Meta:
        db_table = "role"

    def __str__(self):
        return self.nom_role


class UsersManager(BaseUserManager):
    def create_user(self, matricule, password=None, **extra_fields):
        if not matricule:
            raise ValueError("Le matricule est obligatoire.")

        user = self.model(matricule=matricule, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, matricule, password=None, **extra_fields):
        role, _ = Role.objects.get_or_create(
            code_role=Role.RoleCode.ADMIN,
            defaults={
                "nom_role": "Administrateur",
                "description": "Role administrateur Django.",
                "statut": True,
            },
        )
        extra_fields.setdefault("nom_users", "Administrateur Django")
        extra_fields.setdefault("id_role", role)
        extra_fields.setdefault("scope_type", Users.ScopeType.GENERAL)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superuser doit avoir is_superuser=True.")

        return self.create_user(matricule, password, **extra_fields)


class Users(AbstractUser):
    class ScopeType(models.TextChoices):
        GENERAL = "GENERAL", "Général"
        DEPARTEMENT = "DEPARTEMENT", "Département"
        DIRECTION = "DIRECTION", "Direction"

    id_users = models.AutoField(primary_key=True)
    username = None

    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    nom_users = models.CharField(max_length=100)
    matricule = models.CharField(max_length=30, unique=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    id_role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        db_column="id_role",
        related_name="users",
    )

    scope_type = models.CharField(
        max_length=20,
        choices=ScopeType.choices,
        default=ScopeType.GENERAL,
    )

    id_departement = models.ForeignKey(
        "organisation.Departement",
        on_delete=models.SET_NULL,
        db_column="id_departement",
        blank=True,
        null=True,
        related_name="users",
    )

    id_direction = models.ForeignKey(
        "organisation.Direction",
        on_delete=models.SET_NULL,
        db_column="id_direction",
        blank=True,
        null=True,
        related_name="users",
    )

    id_service = models.ForeignKey(
        "organisation.Service",
        on_delete=models.SET_NULL,
        db_column="id_service",
        blank=True,
        null=True,
        related_name="users",
    )

    @property
    def role_code(self):
        if self.id_role:
            return self.id_role.code_role
        return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    USERNAME_FIELD = "matricule"
    REQUIRED_FIELDS = ["nom_users"]

    objects = UsersManager()

    class Meta:
        db_table = "users"

    def clean(self):
        errors = {}

        if self.scope_type == self.ScopeType.DEPARTEMENT and not self.id_departement:
            errors["id_departement"] = "Le département est obligatoire pour un scope DEPARTEMENT."

        if self.scope_type == self.ScopeType.DIRECTION and not self.id_direction:
            errors["id_direction"] = "La direction est obligatoire pour un scope DIRECTION."

        if self.scope_type == self.ScopeType.GENERAL:
            if self.id_departement or self.id_direction or self.id_service:
                errors["scope_type"] = "Un utilisateur GENERAL ne doit pas avoir de périmètre précis."

        if self.id_role and self.id_role.code_role == Role.RoleCode.MAGASIN and self.scope_type == self.ScopeType.GENERAL:
            queryset = Users.objects.filter(
                id_role=self.id_role,
                scope_type=self.ScopeType.GENERAL,
                is_active=True,
            )
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            if self.is_active and queryset.exists():
                errors["scope_type"] = "Il ne peut y avoir qu'un seul magasinier general actif."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.matricule:
            self.matricule = self.matricule.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom_users} - {self.matricule}"
