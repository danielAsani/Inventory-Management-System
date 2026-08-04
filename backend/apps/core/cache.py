from django.core.cache import cache

from apps.core.deletion import CascadeProtectedDeleteMixin


CACHE_SHORT = 30
CACHE_MEDIUM = 60 * 5
CACHE_LONG = 60 * 15


class CachedListRetrieveMixin(CascadeProtectedDeleteMixin):
    cache_timeout = CACHE_MEDIUM

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = super().perform_create(serializer)
        cache.clear()
        return instance

    def perform_update(self, serializer):
        instance = super().perform_update(serializer)
        cache.clear()
        return instance

    def perform_destroy(self, instance):
        result = super().perform_destroy(instance)
        cache.clear()
        return result
