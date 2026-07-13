
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Famille',
            fields=[
                ('id_famille', models.AutoField(primary_key=True, serialize=False)),
                ('code_famille', models.CharField(max_length=20, unique=True)),
                ('nom_famille', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('statut', models.BooleanField(default=True)),
                ('date_creation', models.DateField(default=django.utils.timezone.localdate)),
            ],
            options={
                'db_table': 'famille',
            },
        ),
        migrations.CreateModel(
            name='Fournisseur',
            fields=[
                ('id_fournisseur', models.AutoField(primary_key=True, serialize=False)),
                ('nom_fournisseur', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('adresse', models.CharField(blank=True, max_length=255, null=True)),
                ('rccm', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('nif', models.CharField(blank=True, max_length=30, null=True, unique=True)),
                ('date_creation', models.DateField(default=django.utils.timezone.localdate)),
                ('statut', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'fournisseur',
            },
        ),
        migrations.CreateModel(
            name='UniteMesure',
            fields=[
                ('id_unite', models.AutoField(primary_key=True, serialize=False)),
                ('code_unite', models.CharField(max_length=10, unique=True)),
                ('nom_unite', models.CharField(max_length=30)),
                ('symbole', models.CharField(max_length=10)),
            ],
            options={
                'db_table': 'unite_mesure',
            },
        ),
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id_categorie', models.AutoField(primary_key=True, serialize=False)),
                ('code_categorie', models.CharField(max_length=20, unique=True)),
                ('nom_categorie', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('statut', models.BooleanField(default=True)),
                ('date_creation', models.DateField(default=django.utils.timezone.localdate)),
                ('id_famille', models.ForeignKey(db_column='id_famille', on_delete=django.db.models.deletion.PROTECT, related_name='categories', to='catalogue.famille')),
            ],
            options={
                'db_table': 'categorie',
            },
        ),
    ]
