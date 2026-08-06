import logging

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .notifications import notify_applicant_confirmation, notify_staff_of_application
from .serializers import (
    ClaimResearchApplicationInviteSerializer,
    PublicResearchApplicationSerializer,
)

logger = logging.getLogger(__name__)


class PublicResearchApplicationCreateView(APIView):
    """Anonymous public form submit. No session auth so CSRF is not required."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = PublicResearchApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()

        try:
            notify_staff_of_application(application)
        except Exception:
            logger.exception("Failed to email staff about research application %s", application.pk)

        try:
            notify_applicant_confirmation(application)
        except Exception:
            logger.exception("Failed to email applicant for research application %s", application.pk)

        return Response(
            {
                "id": application.pk,
                "status": application.status,
                "detail": "Application submitted. Forest staff will follow up by email.",
            },
            status=status.HTTP_201_CREATED,
        )


class PublicResearchApplicationInviteClaimView(APIView):
    """Anonymous claim of an approval invite: create username/password + Project."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ClaimResearchApplicationInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_201_CREATED)
