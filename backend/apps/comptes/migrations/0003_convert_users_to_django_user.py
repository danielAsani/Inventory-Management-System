import datetime

import django.utils.timezone
from django.db import migrations, models


def copy_custom_user_fields(apps, schema_editor):
    Users = apps.get_model("comptes", "Users")
    for user in Users.objects.all():
        user.password = user.password_hash
        user.last_login = user.dernier_login
        user.is_active = user.statut
        user.first_name = user.nom_users or ""
        if user.date_ajout:
            user.date_joined = django.utils.timezone.make_aware(
                datetime.datetime.combine(user.date_ajout, datetime.time.min)
            )
        user.save(
            update_fields=[
                "password",
                "last_login",
                "is_active",
                "first_name",
                "date_joined",
            ]
        )


def restore_custom_user_fields(apps, schema_editor):
    Users = apps.get_model("comptes", "Users")
    for user in Users.objects.all():
        user.password_hash = user.password
        user.dernier_login = user.last_login
        user.statut = user.is_active
        if user.date_joined:
            user.date_ajout = user.date_joined.date()
        user.save(update_fields=["password_hash", "dernier_login", "statut", "date_ajout"])


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("comptes", "0002_alter_role_code_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="users",
            name="password",
            field=models.CharField(default="", max_length=128, verbose_name="password"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="users",
            name="last_login",
            field=models.DateTimeField(blank=True, null=True, verbose_name="last login"),
        ),
        migrations.AddField(
            model_name="users",
            name="is_superuser",
            field=models.BooleanField(
                default=False,
                help_text="Designates that this user has all permissions without explicitly assigning them.",
                verbose_name="superuser status",
            ),
        ),
        migrations.AddField(
            model_name="users",
            name="first_name",
            field=models.CharField(blank=True, default="", max_length=150, verbose_name="first name"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="users",
            name="last_name",
            field=models.CharField(blank=True, default="", max_length=150, verbose_name="last name"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="users",
            name="is_staff",
            field=models.BooleanField(
                default=False,
                help_text="Designates whether the user can log into this admin site.",
                verbose_name="staff status",
            ),
        ),
        migrations.AddField(
            model_name="users",
            name="is_active",
            field=models.BooleanField(
                default=True,
                help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                verbose_name="active",
            ),
        ),
        migrations.AddField(
            model_name="users",
            name="date_joined",
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined"),
        ),
        migrations.AddField(
            model_name="users",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="users",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.RunPython(copy_custom_user_fields, restore_custom_user_fields),
        migrations.RemoveField(
            model_name="users",
            name="dernier_login",
        ),
        migrations.RemoveField(
            model_name="users",
            name="password_hash",
        ),
        migrations.RemoveField(
            model_name="users",
            name="statut",
        ),
        migrations.RemoveField(
            model_name="users",
            name="date_ajout",
        ),
        migrations.AlterField(
            model_name="users",
            name="scope_type",
            field=models.CharField(
                choices=[
                    ("GENERAL", "GÃ©nÃ©ral"),
                    ("DEPARTEMENT", "DÃ©partement"),
                    ("DIRECTION", "Direction"),
                    ("SERVICE", "Service"),
                    ("MAGASIN", "Magasin"),
                ],
                default="GENERAL",
                max_length=20,
            ),
        ),
    ]
