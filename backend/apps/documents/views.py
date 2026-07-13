from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import GESTION_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTION_WRITE_ROLES}
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [SearchFilter]
    search_fields = ["type_document", "numero_document", "titre", "chemin_fichier", "mime_type", "observation"]
