"""
URL Configuration for users app
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    user_login,
    user_profile,
    user_logout
)
from .views import (
    password_reset_request,
    password_reset_confirm,
)

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', user_profile, name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', password_reset_request, name='password_reset'),
    path('password-reset/confirm/', password_reset_confirm, name='password_reset_confirm'),
]
