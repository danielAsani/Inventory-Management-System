
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0002_demande_date_finalisation_and_more'),
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='demande',
            name='id_consommable',
            field=models.ForeignKey(blank=True, db_column='id_consommable', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='demandes', to='stock.consommable'),
        ),
        migrations.AddField(
            model_name='demande',
            name='id_materiel',
            field=models.ForeignKey(blank=True, db_column='id_materiel', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='demandes', to='stock.materiel'),
        ),
        migrations.AddField(
            model_name='demande',
            name='quantite_demandee',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
