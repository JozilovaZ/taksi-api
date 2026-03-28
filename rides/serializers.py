from rest_framework import serializers
from accounts.serializers import UserSerializer, DriverProfileSerializer
from .models import PersonalRide, CompanionTrip, SeatBooking, Payment


# ──────────────── SHAXSIY ────────────────

class PersonalRideCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalRide
        fields = (
            'id', 'pickup_address', 'pickup_lat', 'pickup_lng',
            'dropoff_address', 'dropoff_lat', 'dropoff_lng',
        )

    def create(self, validated_data):
        validated_data['passenger'] = self.context['request'].user
        # Oddiy narx hisoblash (1 km = 5000 so'm)
        from math import radians, sin, cos, sqrt, atan2
        lat1 = radians(validated_data['pickup_lat'])
        lat2 = radians(validated_data['dropoff_lat'])
        dlat = lat2 - lat1
        dlng = radians(validated_data['dropoff_lng'] - validated_data['pickup_lng'])
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        distance_km = 6371 * 2 * atan2(sqrt(a), sqrt(1 - a))
        validated_data['distance_km'] = round(distance_km, 2)
        validated_data['price'] = round(max(distance_km * 5000, 10000), 0)
        return super().create(validated_data)


class PersonalRideSerializer(serializers.ModelSerializer):
    passenger = UserSerializer(read_only=True)
    driver = DriverProfileSerializer(read_only=True)

    class Meta:
        model = PersonalRide
        fields = '__all__'


# ──────────────── HAMROH ────────────────

class CompanionTripCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanionTrip
        fields = (
            'id', 'from_address', 'from_lat', 'from_lng',
            'to_address', 'to_lat', 'to_lng',
            'departure_time', 'price_per_seat', 'total_seats',
        )

    def create(self, validated_data):
        validated_data['driver'] = self.context['request'].user.driver_profile
        validated_data['available_seats'] = validated_data['total_seats']
        return super().create(validated_data)


class SeatBookingSerializer(serializers.ModelSerializer):
    passenger = UserSerializer(read_only=True)

    class Meta:
        model = SeatBooking
        fields = '__all__'
        read_only_fields = ('trip', 'passenger', 'total_price', 'status')


class CompanionTripSerializer(serializers.ModelSerializer):
    driver = DriverProfileSerializer(read_only=True)
    bookings = SeatBookingSerializer(many=True, read_only=True)

    class Meta:
        model = CompanionTrip
        fields = '__all__'


class CompanionTripListSerializer(serializers.ModelSerializer):
    driver = DriverProfileSerializer(read_only=True)

    class Meta:
        model = CompanionTrip
        fields = (
            'id', 'driver', 'from_address', 'to_address',
            'departure_time', 'price_per_seat', 'total_seats',
            'available_seats', 'status',
        )


class BookSeatSerializer(serializers.Serializer):
    seats_count = serializers.IntegerField(min_value=1, default=1)


# ──────────────── TO'LOV ────────────────

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('user', 'amount', 'status')
