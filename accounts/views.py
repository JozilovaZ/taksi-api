from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import DriverProfile
from .serializers import (
    RegisterSerializer, UserSerializer,
    DriverProfileSerializer, DriverLocationUpdateSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Yangi foydalanuvchi ro'yxatdan o'tkazish (yo'lovchi yoki haydovchi)"""
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Foydalanuvchi profilini ko'rish va tahrirlash"""
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class DriverProfileView(generics.RetrieveUpdateAPIView):
    """Haydovchi profilini ko'rish va tahrirlash (mashina, reyting, lokatsiya)"""
    serializer_class = DriverProfileSerializer

    def get_object(self):
        return self.request.user.driver_profile


@swagger_auto_schema(
    method='post',
    request_body=DriverLocationUpdateSerializer,
    operation_description="Haydovchi hozirgi lokatsiyasini yangilaydi",
    responses={200: openapi.Response('Muvaffaqiyatli', examples={
        'application/json': {'status': 'location updated'}
    })}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_driver_location(request):
    serializer = DriverLocationUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    profile = request.user.driver_profile
    profile.current_lat = serializer.validated_data['lat']
    profile.current_lng = serializer.validated_data['lng']
    profile.save(update_fields=['current_lat', 'current_lng'])
    return Response({'status': 'location updated'})


@swagger_auto_schema(
    method='post',
    request_body=None,
    operation_description="Haydovchi bo'sh/band holatini almashtiradi",
    responses={200: openapi.Response('Muvaffaqiyatli', examples={
        'application/json': {'is_available': True}
    })}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_availability(request):
    profile = request.user.driver_profile
    profile.is_available = not profile.is_available
    profile.save(update_fields=['is_available'])
    return Response({'is_available': profile.is_available})
