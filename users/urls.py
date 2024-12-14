from django.urls import path ,include

from .views import (AuthCreateAPIView, VerifyCreateAPIView,
                    SignOutAPIView, UserDetailsUpdateAPIView,
                    TokenCreateAPIView, DeleteDestroyAPIView)

urlpatterns = [
    path("auth/", include([
        path("", AuthCreateAPIView.as_view(), name="auth"),
        path("verify/", VerifyCreateAPIView.as_view(), name="verify"),
        path("details/", UserDetailsUpdateAPIView.as_view(), name="details"),
        path("token/", TokenCreateAPIView.as_view(), name="token"),
        # path("sign-out/", SignOutAPIView.as_view(), name="signout")
    ])),
    path("delete/", DeleteDestroyAPIView.as_view(), name="delete"),
]