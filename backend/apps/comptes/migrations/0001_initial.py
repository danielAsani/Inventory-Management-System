
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organisation', '0001_initial'),
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id_role', models.AutoField(primary_key=True, serialize=False)),
                ('code_role', models.CharField(max_length=30, unique=True)),
                ('nom_role', models.CharField(max_length=30)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('statut', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'role',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id_users', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(blank=True, max_length=100, null=True, unique=True)),
                ('nom_users', models.CharField(max_length=100)),
                ('matricule', models.CharField(max_length=30, unique=True)),
                ('telephone', models.CharField(blank=True, max_length=20, null=True)),
                ('password_hash', models.CharField(max_length=255)),
                ('statut', models.BooleanField(default=True)),
                ('dernier_login', models.DateTimeField(blank=True, null=True)),
                ('date_ajout', models.DateField(default=django.utils.timezone.localdate)),
                ('scope_type', models.CharField(choices=[('GENERAL', 'GÃ©nÃ©ral'), ('DEPARTEMENT', 'DÃ©partement'), ('DIRECTION', 'Direction'), ('SERVICE', 'Service'), ('MAGASIN', 'Magasin')], default='GENERAL', max_length=20)),
                ('id_departement', models.ForeignKey(blank=True, db_column='id_departement', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='organisation.departement')),
                ('id_direction', models.ForeignKey(blank=True, db_column='id_direction', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='organisation.direction')),
                ('id_magasin', models.ForeignKey(blank=True, db_column='id_magasin', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='stock.magasin')),
                ('id_role', models.ForeignKey(db_column='id_role', on_delete=django.db.models.deletion.PROTECT, related_name='users', to='comptes.role')),
                ('id_service', models.ForeignKey(blank=True, db_column='id_service', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='organisation.service')),
            ],
            options={
                'db_table': 'users',
            },
        ),
    ]
