from rest_framework.filters import SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet

from apps.core.deletion import CascadeProtectedDeleteMixin
from apps.core.permissions import GESTION_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(CascadeProtectedDeleteMixin, ModelViewSet):
    permission_classes = [RoleBasedPermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTION_WRITE_ROLES}
    queryset = Document.objects.select_related("id_materiel", "id_consommable", "cree_par").all()
    serializer_class = DocumentSerializer
    filter_backends = [SearchFilter]
    search_fields = ["type_document", "numero_document", "titre", "chemin_fichier", "observation"]

    def get_queryset(self):
        queryset = super().get_queryset()
        type_document = self.request.query_params.get("type_document")
        if type_document:
            queryset = queryset.filter(type_document=type_document)
        return queryset
