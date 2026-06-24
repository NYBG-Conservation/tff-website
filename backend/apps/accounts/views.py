from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile
from .permissions import IsInternalSuperadmin
from .roles import count_internal_superadmins, is_internal_superadmin
from .serializers import AssignRoleSerializer, CurrentUserSerializer

User = get_user_model()


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)


class CsrfTokenView(APIView):
    permission_classes = []
    authentication_classes = []

    @ensure_csrf_cookie
    def get(self, request):
        return Response({"detail": "CSRF cookie set"})


class AssignRoleView(APIView):
    """Assign a platform role (including internal_superadmin) to a user. Internal superadmins only."""

    permission_classes = [IsAuthenticated, IsInternalSuperadmin]

    def post(self, request):
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        new_role = serializer.validated_data["role"]
        organization = serializer.validated_data.get("organization")

        target_user = User.objects.get(username=username)
        profile = target_user.profile

        if (
            profile.role == UserProfile.Role.INTERNAL_SUPERADMIN
            and new_role != UserProfile.Role.INTERNAL_SUPERADMIN
            and count_internal_superadmins() <= 1
        ):
            return Response(
                {"detail": "Cannot demote the only internal superadmin."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile.role = new_role
        profile.organization = organization
        profile.save(update_fields=["role", "organization"])

        return Response(
            {
                "username": target_user.username,
                "role": profile.role,
                "organization_id": profile.organization_id,
                "organization_name": profile.organization.name if profile.organization_id else None,
            }
        )
