from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organisation", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="direction",
            name="code_direction",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name="service",
            name="code_service",
            field=models.CharField(max_length=20),
        ),
        migrations.AddConstraint(
            model_name="direction",
            constraint=models.UniqueConstraint(
                fields=("id_departement", "code_direction"),
                name="uniq_direction_code_par_departement",
            ),
        ),
        migrations.AddConstraint(
            model_name="service",
            constraint=models.UniqueConstraint(
                fields=("id_direction", "code_service"),
                name="uniq_service_code_par_direction",
            ),
        ),
    ]
