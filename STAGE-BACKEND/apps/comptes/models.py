from django.db import models


class Role(models.Model):
    id_role = models.FloatField(primary_key=True)
    nom_role = models.CharField(max_length=30)
    description = models.CharField(max_length=255, blank=True, null=True)
    statut = models.BooleanField()
    code_role = models.CharField(unique=True, max_length=30)

    class Meta:
        managed = False
        db_table = 'ROLE'


class Users(models.Model):
    id_users = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    nom_users = models.CharField(max_length=100)
    matricule = models.CharField(max_length=30)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    password_hash = models.CharField(max_length=255)
    statut = models.BooleanField()
    dernier_login = models.DateTimeField(blank=True, null=True)
    date_ajout = models.DateField()
    id_role = models.ForeignKey(
        'comptes.Role',
        models.DO_NOTHING,
        db_column='id_role',
        blank=True,
        null=True,
    )
    scope_type = models.CharField(max_length=20, blank=True, null=True)
    id_departement = models.ForeignKey(
        'organisation.Departement',
        models.DO_NOTHING,
        db_column='id_departement',
        blank=True,
        null=True,
    )
    id_direction = models.ForeignKey(
        'organisation.Direction',
        models.DO_NOTHING,
        db_column='id_direction',
        blank=True,
        null=True,
    )
    id_service = models.ForeignKey(
        'organisation.Service',
        models.DO_NOTHING,
        db_column='id_service',
        blank=True,
        null=True,
    )
    id_magasin = models.ForeignKey(
        'stock.Magasin',
        models.DO_NOTHING,
        db_column='id_magasin',
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = 'USERS'

    @property
    def is_authenticated(self):
        return True

    @property
    def role_code(self):
        role = self.id_role
        if not role:
            return None

        raw_role = role.code_role or role.nom_role
        if not raw_role:
            return None

        raw_role = raw_role.upper()
        if 'ADMIN' in raw_role:
            return 'ADMIN'
        if 'GESTIONNAIRE' in raw_role:
            return 'GESTIONNAIRE'
        if 'MAGASINIER' in raw_role:
            return 'MAGASINIER'
        if 'AUDITEUR' in raw_role or 'AUDITOR' in raw_role:
            return 'AUDITEUR'
        return raw_role
