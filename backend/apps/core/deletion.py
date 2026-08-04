from django.core.cache import cache
from django.db import transaction
from django.db.models import ProtectedError


CASCADE_PARAM_VALUES = {"1", "true", "yes", "oui"}
CASCADE_BLOCKED_TABLES = {"users", "role"}


def wants_cascade_delete(request):
    return str(request.query_params.get("cascade", "")).lower() in CASCADE_PARAM_VALUES


def force_delete_with_protected_relations(instance, seen=None):
    if instance._meta.db_table in CASCADE_BLOCKED_TABLES:
        raise ProtectedError(
            "La suppression en cascade est desactivee pour les comptes et roles.",
            {instance},
        )

    seen = seen or set()
    key = (instance._meta.label_lower, instance.pk)
    if key in seen:
        return
    seen.add(key)

    try:
        instance.delete()
    except ProtectedError as exc:
        for protected_object in exc.protected_objects:
            force_delete_with_protected_relations(protected_object, seen)
        instance.delete()


class CascadeProtectedDeleteMixin:
    def perform_destroy(self, instance):
        if not wants_cascade_delete(self.request):
            return super().perform_destroy(instance)

        with transaction.atomic():
            force_delete_with_protected_relations(instance)
            cache.clear()
