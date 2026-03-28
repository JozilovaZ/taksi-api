from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('driver-profile/', views.DriverProfileView.as_view(), name='driver-profile'),
    path('driver/location/', views.update_driver_location, name='driver-location'),
    path('driver/toggle-availability/', views.toggle_availability, name='toggle-availability'),
]
