from rest_framework.filters import SearchFilter
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.viewsets import ModelViewSet
from apps.core.cache import CACHE_MEDIUM, CachedListRetrieveMixin
from apps.core.filters import parse_bool
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

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = parse_bool(self.request.query_params.get("statut"))
        if statut is not None:
            queryset = queryset.filter(statut=statut)
        return queryset


class CategorieViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = Categorie.objects.select_related("id_famille").all()
    serializer_class = CategorieSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_categorie", "nom_categorie", "id_famille__nom_famille", "description"]

    def get_queryset(self):
        queryset = super().get_queryset()
        id_famille = self.request.query_params.get("id_famille")
        statut = parse_bool(self.request.query_params.get("statut"))
        if id_famille:
            queryset = queryset.filter(id_famille_id=id_famille)
        if statut is not None:
            queryset = queryset.filter(statut=statut)
        return queryset


class UniteMesureViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = UniteMesure.objects.all()
    serializer_class = UniteMesureSerializer
    filter_backends = [SearchFilter]
    search_fields = ["code_unite", "nom_unite", "symbole"]

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed("POST", detail="Les unites de mesure sont un referentiel systeme.")

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PUT", detail="Les unites de mesure sont un referentiel systeme.")

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed("PATCH", detail="Les unites de mesure sont un referentiel systeme.")

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE", detail="Les unites de mesure sont un referentiel systeme.")


class FournisseurViewSet(CachedListRetrieveMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES}
    cache_timeout = CACHE_MEDIUM
    queryset = Fournisseur.objects.prefetch_related("materiels").all()
    serializer_class = FournisseurSerializer
    filter_backends = [SearchFilter]
    search_fields = ["nom_fournisseur", "email", "rccm", "nif"]

    def get_queryset(self):
        queryset = super().get_queryset()
        statut = parse_bool(self.request.query_params.get("statut"))
        if statut is not None:
            queryset = queryset.filter(statut=statut)
        return queryset
