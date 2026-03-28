from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DriverProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'password', 'role')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            phone=validated_data['phone'],
            password=validated_data['password'],
            role=validated_data.get('role', 'passenger'),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'role')


class DriverProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DriverProfile
        fields = (
            'id', 'user', 'license_plate', 'car_model', 'car_color',
            'total_seats', 'rating', 'is_available', 'current_lat', 'current_lng',
        )


class DriverLocationUpdateSerializer(serializers.Serializer):
    lat = serializers.FloatField()
    lng = serializers.FloatField()
