from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import GESTIONNAIRE_WRITE_ROLES, READ_ALL_ROLES, RoleBasedPermission
from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(ModelViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {'read': READ_ALL_ROLES, 'create': GESTIONNAIRE_WRITE_ROLES}
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
