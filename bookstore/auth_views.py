from rest_framework import permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class LoginView(ObtainAuthToken):
    throttle_classes = [LoginRateThrottle]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)