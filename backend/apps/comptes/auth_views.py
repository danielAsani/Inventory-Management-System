from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import READ_ALL_ROLES, RoleBasedPermission
from .auth_serializers import ChangePasswordSerializer, LoginSerializer, RefreshSerializer, UserProfileSerializer
from .models import Users


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        Users.objects.filter(id_users=user.id_users).update(last_login=timezone.now())

        return Response(
            {
                "access": serializer.validated_data["tokens"]["access"],
                "refresh": serializer.validated_data["tokens"]["refresh"],
                "user": UserProfileSerializer(user).data,
            }
        )


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"access": serializer.validated_data["access"]})


class MeView(APIView):
    permission_classes = [RoleBasedPermission]
    role_permissions = {"read": READ_ALL_ROLES}

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = [RoleBasedPermission]
    role_permissions = {"read": READ_ALL_ROLES, "write": READ_ALL_ROLES}

    def post(self, request):
        return Response({"detail": "Deconnexion reussie. Supprimez le token cote frontend."})


class ChangePasswordView(APIView):
    permission_classes = [RoleBasedPermission]
    role_permissions = {"write": READ_ALL_ROLES}

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Mot de passe modifie avec succes."})
