"""Authentication API URL patterns.

Defines URL routes for user authentication endpoints including
registration, login, token refresh, and logout functionality.
"""
from django.urls import path

from .views import RegistrationView, LoginView, CookieTokenRefreshView, LogoutView


urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='token_logout'),
]