from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CurrentUserSerializer


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
