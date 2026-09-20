from django.urls import path

from .views import (
    LogoutView,
    MeView,
    RegisterView,
    ThrottledTokenObtainPairView,
    ThrottledTokenRefreshView,
    ThrottledTokenVerifyView,
)


app_name = "users"

urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "token/",
        ThrottledTokenObtainPairView.as_view(),
        name="token-obtain-pair",
    ),
    path(
        "token/refresh/",
        ThrottledTokenRefreshView.as_view(),
        name="token-refresh",
    ),
    path(
        "token/verify/",
        ThrottledTokenVerifyView.as_view(),
        name="token-verify",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),
]