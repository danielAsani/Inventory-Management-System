from rest_framework.viewsets import ModelViewSet
from apps.core.cache import CACHE_MEDIUM, CachedListRetrieveMixin
from apps.core.permissions import GESTIONNAIRE_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Famille, Categorie, UniteMesure, Fournisseur
from .serializers import (
    FamilleSerializer,
    CategorieSerializer,
    UniteMesureSerializer,
    FournisseurSerializer,
)


class FamilleViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTIONNAIRE_WRITE_ROLES, 'update': GESTIONNAIRE_WRITE_ROLES, 'partial_update': GESTIONNAIRE_WRITE_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = Famille.objects.all()
    serializer_class = FamilleSerializer


class CategorieViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTIONNAIRE_WRITE_ROLES, 'update': GESTIONNAIRE_WRITE_ROLES, 'partial_update': GESTIONNAIRE_WRITE_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer


class UniteMesureViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTIONNAIRE_WRITE_ROLES, 'update': GESTIONNAIRE_WRITE_ROLES, 'partial_update': GESTIONNAIRE_WRITE_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = UniteMesure.objects.all()
    serializer_class = UniteMesureSerializer


class FournisseurViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTIONNAIRE_WRITE_ROLES, 'update': GESTIONNAIRE_WRITE_ROLES, 'partial_update': GESTIONNAIRE_WRITE_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
