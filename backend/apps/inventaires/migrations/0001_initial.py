
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('comptes', '0001_initial'),
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventaire',
            fields=[
                ('id_inventaire', models.AutoField(primary_key=True, serialize=False)),
                ('code_inventaire', models.CharField(max_length=30, unique=True)),
                ('entite_type', models.CharField(choices=[('DEPARTEMENT', 'DÃ©partement'), ('DIRECTION', 'Direction'), ('SERVICE', 'Service'), ('MAGASIN', 'Magasin')], max_length=20)),
                ('entite_id', models.PositiveIntegerField()),
                ('type_inventaire', models.CharField(choices=[('GENERAL', 'GÃ©nÃ©ral'), ('PARTIEL', 'Partiel'), ('PERIODIQUE', 'PÃ©riodique'), ('EXCEPTIONNEL', 'Exceptionnel')], default='GENERAL', max_length=20)),
                ('date_debut', models.DateField(default=django.utils.timezone.localdate)),
                ('date_fin', models.DateField(blank=True, null=True)),
                ('statut', models.CharField(choices=[('EN_COURS', 'En cours'), ('TERMINE', 'TerminÃ©'), ('ANNULE', 'AnnulÃ©')], default='EN_COURS', max_length=20)),
                ('observation', models.CharField(blank=True, max_length=500, null=True)),
                ('effectue_par', models.ForeignKey(blank=True, db_column='effectue_par', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='inventaires_effectues', to='comptes.users')),
            ],
            options={
                'db_table': 'inventaire',
            },
        ),
        migrations.CreateModel(
            name='InventaireDetail',
            fields=[
                ('id_detail', models.AutoField(primary_key=True, serialize=False)),
                ('quantite_theorique', models.PositiveIntegerField(default=0)),
                ('quantite_reelle', models.PositiveIntegerField(default=0)),
                ('ecart', models.IntegerField(default=0)),
                ('observation', models.CharField(blank=True, max_length=500, null=True)),
                ('id_consommable', models.ForeignKey(blank=True, db_column='id_consommable', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='details_inventaire', to='stock.consommable')),
                ('id_inventaire', models.ForeignKey(db_column='id_inventaire', on_delete=django.db.models.deletion.CASCADE, related_name='details', to='inventaires.inventaire')),
                ('id_materiel', models.ForeignKey(blank=True, db_column='id_materiel', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='details_inventaire', to='stock.materiel')),
            ],
            options={
                'db_table': 'inventaire_detail',
            },
        ),
    ]
