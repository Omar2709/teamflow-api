from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from .serializers import (
    CurrentUserResponseSerializer,
    LogoutRequestSerializer,
    LogoutResponseSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class MeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        tags=["auth"],
        summary="Obtener usuario autenticado",
        description=(
            "Devuelve la información del usuario "
            "autenticado mediante JWT."
        ),
        responses={
            200: CurrentUserResponseSerializer,
        },
    )
    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response({
            "message": "Usuario autenticado.",
            "data": serializer.data,
        })


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(
        tags=["auth"],
        summary="Cerrar sesión",
        description=(
            "Invalida el refresh token proporcionado "
            "para cerrar la sesión del usuario."
        ),
        request=LogoutRequestSerializer,
        responses={
            200: LogoutResponseSerializer,
            400: LogoutResponseSerializer,
        },
    )
    
    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "message": (
                        "Debes proporcionar el refresh token."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {
                    "message": (
                        "El refresh token no es válido "
                        "o ya fue invalidado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Sesión cerrada correctamente."},
            status=status.HTTP_200_OK,
        )