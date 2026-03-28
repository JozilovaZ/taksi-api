from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import PersonalRide, CompanionTrip, SeatBooking, Payment
from .serializers import (
    PersonalRideCreateSerializer, PersonalRideSerializer,
    CompanionTripCreateSerializer, CompanionTripSerializer,
    CompanionTripListSerializer, BookSeatSerializer,
    SeatBookingSerializer, PaymentSerializer,
)

ride_status_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['status'],
    properties={
        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['in_progress', 'completed', 'cancelled']),
        'payment_method': openapi.Schema(type=openapi.TYPE_STRING, enum=['cash', 'card'], default='cash'),
    }
)

payment_method_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'payment_method': openapi.Schema(type=openapi.TYPE_STRING, enum=['cash', 'card'], default='cash'),
    }
)


# ══════════════════ SHAXSIY REJIM ══════════════════

class PersonalRideCreateView(generics.CreateAPIView):
    """Yo'lovchi taksi chaqiradi — narx va masofa avtomatik hisoblanadi"""
    serializer_class = PersonalRideCreateSerializer


class PersonalRideDetailView(generics.RetrieveAPIView):
    """Shaxsiy safar tafsilotlari — haydovchi, narx, status"""
    serializer_class = PersonalRideSerializer
    queryset = PersonalRide.objects.all()


class MyPersonalRidesView(generics.ListAPIView):
    """Yo'lovchining barcha shaxsiy safarlari ro'yxati"""
    serializer_class = PersonalRideSerializer

    def get_queryset(self):
        return PersonalRide.objects.filter(passenger=self.request.user)


@swagger_auto_schema(
    method='post',
    request_body=None,
    operation_description="Haydovchi kutayotgan buyurtmani qabul qiladi",
    responses={200: PersonalRideSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_personal_ride(request, pk):
    ride = PersonalRide.objects.get(pk=pk)
    if ride.status != 'requested':
        return Response({'error': 'Bu buyurtma allaqachon qabul qilingan'}, status=400)
    ride.driver = request.user.driver_profile
    ride.status = 'accepted'
    ride.save()
    return Response(PersonalRideSerializer(ride).data)


@swagger_auto_schema(
    method='post',
    request_body=ride_status_body,
    operation_description="Haydovchi safar statusini o'zgartiradi. 'completed' bo'lsa to'lov avtomatik yaratiladi",
    responses={200: PersonalRideSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_ride_status(request, pk):
    ride = PersonalRide.objects.get(pk=pk)
    new_status = request.data.get('status')
    if new_status not in ('in_progress', 'completed', 'cancelled'):
        return Response({'error': 'Noto\'g\'ri status'}, status=400)
    ride.status = new_status
    ride.save()

    if new_status == 'completed' and ride.price:
        Payment.objects.create(
            user=ride.passenger,
            personal_ride=ride,
            amount=ride.price,
            method=request.data.get('payment_method', 'cash'),
            status='paid',
        )

    return Response(PersonalRideSerializer(ride).data)


@swagger_auto_schema(
    method='get',
    operation_description="Haydovchi uchun kutayotgan (requested) buyurtmalar ro'yxati",
    responses={200: PersonalRideSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_rides_for_driver(request):
    rides = PersonalRide.objects.filter(status='requested')
    return Response(PersonalRideSerializer(rides, many=True).data)


# ══════════════════ HAMROH REJIM ══════════════════

class CompanionTripCreateView(generics.CreateAPIView):
    """Haydovchi yangi hamroh safar e'lon qiladi (yo'nalish, vaqt, narx, o'rindiqlar)"""
    serializer_class = CompanionTripCreateSerializer


class CompanionTripListView(generics.ListAPIView):
    """Faol hamroh safarlarni qidirish. Filter: ?to=samarqand&from=toshkent"""
    serializer_class = CompanionTripListSerializer

    to_param = openapi.Parameter('to', openapi.IN_QUERY, description="Manzil bo'yicha qidirish", type=openapi.TYPE_STRING)
    from_param = openapi.Parameter('from', openapi.IN_QUERY, description="Qayerdan — boshlang'ich manzil", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[to_param, from_param])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = CompanionTrip.objects.filter(status='active', available_seats__gt=0)
        to_address = self.request.query_params.get('to')
        from_address = self.request.query_params.get('from')
        if to_address:
            qs = qs.filter(to_address__icontains=to_address)
        if from_address:
            qs = qs.filter(from_address__icontains=from_address)
        return qs


class CompanionTripDetailView(generics.RetrieveAPIView):
    """Safar tafsilotlari — haydovchi ma'lumotlari, o'rindiqlar, bookinglar ro'yxati"""
    serializer_class = CompanionTripSerializer
    queryset = CompanionTrip.objects.all()


@swagger_auto_schema(
    method='post',
    request_body=BookSeatSerializer,
    operation_description="Yo'lovchi hamroh safarida o'rindiq band qiladi",
    responses={201: SeatBookingSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_seat(request, pk):
    serializer = BookSeatSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    seats_count = serializer.validated_data['seats_count']

    with transaction.atomic():
        trip = CompanionTrip.objects.select_for_update().get(pk=pk)

        if trip.status != 'active':
            return Response({'error': 'Bu safar faol emas'}, status=400)
        if trip.available_seats < seats_count:
            return Response(
                {'error': f'Faqat {trip.available_seats} ta bo\'sh o\'rindiq bor'},
                status=400,
            )

        total_price = trip.price_per_seat * seats_count

        booking = SeatBooking.objects.create(
            trip=trip,
            passenger=request.user,
            seats_count=seats_count,
            total_price=total_price,
        )

        trip.available_seats -= seats_count
        if trip.available_seats == 0:
            trip.status = 'full'
        trip.save()

    return Response(SeatBookingSerializer(booking).data, status=201)


@swagger_auto_schema(
    method='post',
    request_body=payment_method_body,
    operation_description="Haydovchi bookingni tasdiqlaydi va to'lov yaratiladi",
    responses={200: SeatBookingSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_booking(request, pk):
    booking = SeatBooking.objects.get(pk=pk)
    if booking.trip.driver.user != request.user:
        return Response({'error': 'Ruxsat yo\'q'}, status=403)
    booking.status = 'confirmed'
    booking.save()

    Payment.objects.create(
        user=booking.passenger,
        seat_booking=booking,
        amount=booking.total_price,
        method=request.data.get('payment_method', 'cash'),
        status='pending',
    )

    return Response(SeatBookingSerializer(booking).data)


@swagger_auto_schema(
    method='post',
    request_body=None,
    operation_description="Yo'lovchi yoki haydovchi bookingni bekor qiladi. O'rindiqlar qaytariladi",
    responses={200: SeatBookingSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, pk):
    booking = SeatBooking.objects.get(pk=pk)
    if request.user != booking.passenger and request.user != booking.trip.driver.user:
        return Response({'error': 'Ruxsat yo\'q'}, status=403)

    with transaction.atomic():
        booking.status = 'cancelled'
        booking.save()
        trip = CompanionTrip.objects.select_for_update().get(pk=booking.trip_id)
        trip.available_seats += booking.seats_count
        if trip.status == 'full':
            trip.status = 'active'
        trip.save()

    return Response(SeatBookingSerializer(booking).data)


@swagger_auto_schema(
    method='post',
    request_body=ride_status_body,
    operation_description="Haydovchi hamroh safar statusini o'zgartiradi. 'completed' bo'lsa barcha to'lovlar 'paid' bo'ladi",
    responses={200: CompanionTripSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_trip_status(request, pk):
    trip = CompanionTrip.objects.get(pk=pk)
    if trip.driver.user != request.user:
        return Response({'error': 'Ruxsat yo\'q'}, status=403)
    new_status = request.data.get('status')
    if new_status not in ('in_progress', 'completed', 'cancelled'):
        return Response({'error': 'Noto\'g\'ri status'}, status=400)
    trip.status = new_status
    trip.save()

    if new_status == 'completed':
        trip.bookings.filter(status='confirmed').update(status='confirmed')
        Payment.objects.filter(
            seat_booking__trip=trip, status='pending'
        ).update(status='paid')

    return Response(CompanionTripSerializer(trip).data)


# ══════════════════ TO'LOVLAR ══════════════════

class MyPaymentsView(generics.ListAPIView):
    """Foydalanuvchining barcha to'lovlari ro'yxati (shaxsiy va hamroh)"""
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
