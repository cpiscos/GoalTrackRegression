from django.urls import path

from authentication import views

urlpatterns = [
    path("login/", views.login_view),
    path("register/", views.register_view),
    path("logout/", views.logout_view),
    path("authenticated/", views.authenticated_user),
    path("user/", views.authenticated_user),
    path("csrf/", views.csrf_cookie),
]