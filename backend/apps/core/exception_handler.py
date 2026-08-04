from collections import Counter

from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def _protected_error_message(exc):
    protected_objects = getattr(exc, "protected_objects", None) or []
    model_counts = Counter(obj._meta.verbose_name.title() for obj in protected_objects)

    if not model_counts:
        return "Impossible de supprimer cet enregistrement car il est encore utilise ailleurs."

    dependencies = ", ".join(
        f"{model_name} ({count})"
        for model_name, count in sorted(model_counts.items())
    )
    return (
        "Impossible de supprimer cet enregistrement car il est encore utilise par: "
        f"{dependencies}. Supprimez ou modifiez d'abord ces elements lies."
    )


def custom_exception_handler(exc, context):
    if isinstance(exc, ProtectedError):
        return Response(
            {
                "code": "protected_delete",
                "cascade_available": True,
                "detail": _protected_error_message(exc),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return drf_exception_handler(exc, context)
