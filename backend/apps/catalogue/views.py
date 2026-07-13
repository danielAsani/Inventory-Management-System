from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from apps.core.cache import CACHE_MEDIUM, CachedListRetrieveMixin
from apps.core.permissions import READ_ALL_ROLES, RoleBasedPermission
from .models import Famille, Categorie, UniteMesure, Fournisseur
from .serializers import (
    FamilleSerializer,
    CategorieSerializer,
    UniteMesureSerializer,
    FournisseurSerializer,
)


class FamilleViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = Famille.objects.all()
    serializer_class = FamilleSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_famille", "nom_famille", "description"]


class CategorieViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_categorie", "nom_categorie", "description"]


class UniteMesureViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = UniteMesure.objects.all()
    serializer_class = UniteMesureSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_unite", "nom_unite", "symbole"]


class FournisseurViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    filter_backends = [SearchFilter]
    search_fields = ["nom_fournisseur", "email", "rccm", "nif"]
