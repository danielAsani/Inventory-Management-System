
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comptes', '0001_initial'),
        ('demandes', '0001_initial'),
        ('organisation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='demande',
            name='date_finalisation',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='demande',
            name='date_validation_departement',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='demande',
            name='id_direction_demandeuse',
            field=models.ForeignKey(blank=True, db_column='id_direction_demandeuse', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='demandes_emises', to='organisation.direction'),
        ),
        migrations.AddField(
            model_name='demande',
            name='id_magasinier_finalisateur',
            field=models.ForeignKey(blank=True, db_column='id_magasinier_finalisateur', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='demandes_finalisees_magasin', to='comptes.users'),
        ),
        migrations.AddField(
            model_name='demande',
            name='id_service_destinataire',
            field=models.ForeignKey(blank=True, db_column='id_service_destinataire', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='demandes_destinees', to='organisation.service'),
        ),
        migrations.AddField(
            model_name='demande',
            name='id_validateur_departement',
            field=models.ForeignKey(blank=True, db_column='id_validateur_departement', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='demandes_validees_departement', to='comptes.users'),
        ),
        migrations.AddField(
            model_name='demande',
            name='motif_rejet',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='demande',
            name='origine_type',
            field=models.CharField(choices=[('DEPARTEMENT', 'Departement'), ('DIRECTION', 'Direction'), ('SERVICE', 'Service'), ('MAGASIN', 'Magasin')], default='DIRECTION', max_length=20),
        ),
        migrations.AlterField(
            model_name='demande',
            name='statut',
            field=models.CharField(choices=[('EN_ATTENTE_DEPARTEMENT', 'En attente departement'), ('EN_TRAITEMENT_MAGASIN', 'En traitement magasin'), ('TRAITEE', 'Traitee'), ('REJETEE', 'Rejetee'), ('ANNULEE', 'Annulee')], default='EN_ATTENTE_DEPARTEMENT', max_length=30),
        ),
        migrations.AlterField(
            model_name='demande',
            name='type_demande',
            field=models.CharField(choices=[('ACHAT', 'Achat'), ('REAPPROVISIONNEMENT', 'Reapprovisionnement'), ('REPARATION', 'Reparation'), ('AUTRE', 'Autre')], max_length=30),
        ),
    ]
