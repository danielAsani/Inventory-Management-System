
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('comptes', '0001_initial'),
        ('organisation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Demande',
            fields=[
                ('id_demande', models.AutoField(primary_key=True, serialize=False)),
                ('code_demande', models.CharField(max_length=30, unique=True)),
                ('origine_type', models.CharField(choices=[('DEPARTEMENT', 'DÃ©partement'), ('DIRECTION', 'Direction'), ('SERVICE', 'Service'), ('MAGASIN', 'Magasin')], default='DEPARTEMENT', max_length=20)),
                ('origine_id', models.PositiveIntegerField(blank=True, null=True)),
                ('type_demande', models.CharField(choices=[('ACHAT', 'Achat'), ('REAPPROVISIONNEMENT', 'RÃ©approvisionnement'), ('REPARATION', 'RÃ©paration'), ('AUTRE', 'AUTRE')], max_length=30)),
                ('statut', models.CharField(choices=[('EN_ATTENTE', 'En attente'), ('VALIDEE', 'ValidÃ©e'), ('REJETEE', 'RejetÃ©e'), ('TRAITEE', 'TraitÃ©e'), ('ANNULEE', 'AnnulÃ©e')], default='EN_ATTENTE', max_length=20)),
                ('date_demande', models.DateField(default=django.utils.timezone.localdate)),
                ('observation', models.CharField(blank=True, max_length=500, null=True)),
                ('id_demandeur', models.ForeignKey(db_column='id_demandeur', on_delete=django.db.models.deletion.PROTECT, related_name='demandes', to='comptes.users')),
                ('id_departement', models.ForeignKey(db_column='id_departement', on_delete=django.db.models.deletion.PROTECT, related_name='demandes', to='organisation.departement')),
            ],
            options={
                'db_table': 'demande',
            },
        ),
    ]
