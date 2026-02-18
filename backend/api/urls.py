from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('sessions/', views.SessionListView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session-detail'),
    path('generate/', views.GenerateCodeView.as_view(), name='generate-code'),
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
]
