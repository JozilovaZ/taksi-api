from django.db import models
from accounts.models import User, DriverProfile


class PersonalRide(models.Model):
    """Shaxsiy rejim — Yandex Go kabi 1 yo'lovchi 1 haydovchi"""
    STATUS_CHOICES = (
        ('requested', 'So\'ralgan'),
        ('accepted', 'Qabul qilingan'),
        ('in_progress', 'Yo\'lda'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
    )

    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_rides')
    driver = models.ForeignKey(DriverProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='personal_rides')

    pickup_address = models.CharField(max_length=255)
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    dropoff_address = models.CharField(max_length=255)
    dropoff_lat = models.FloatField()
    dropoff_lng = models.FloatField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Shaxsiy: {self.passenger} -> {self.dropoff_address} ({self.status})"


class CompanionTrip(models.Model):
    """Hamroh rejim — haydovchi yo'nalish e'lon qiladi, yo'lovchilar o'rindiq band qiladi"""
    STATUS_CHOICES = (
        ('active', 'Faol'),
        ('full', 'To\'lgan'),
        ('in_progress', 'Yo\'lda'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
    )

    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE, related_name='companion_trips')

    from_address = models.CharField(max_length=255)
    from_lat = models.FloatField()
    from_lng = models.FloatField()
    to_address = models.CharField(max_length=255)
    to_lat = models.FloatField()
    to_lng = models.FloatField()

    departure_time = models.DateTimeField()
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-departure_time']

    def __str__(self):
        return f"Hamroh: {self.from_address} -> {self.to_address} ({self.available_seats} bo'sh)"


class SeatBooking(models.Model):
    """Hamroh safarida o'rindiq band qilish"""
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlangan'),
        ('cancelled', 'Bekor qilingan'),
    )

    trip = models.ForeignKey(CompanionTrip, on_delete=models.CASCADE, related_name='bookings')
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seat_bookings')
    seats_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trip', 'passenger')

    def __str__(self):
        return f"{self.passenger} - {self.seats_count} o'rindiq ({self.status})"


class Payment(models.Model):
    """To'lov — shaxsiy va hamroh uchun umumiy"""
    METHOD_CHOICES = (
        ('cash', 'Naqd'),
        ('card', 'Karta'),
    )
    STATUS_CHOICES = (
        ('pending', 'Kutilmoqda'),
        ('paid', 'To\'langan'),
        ('refunded', 'Qaytarilgan'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    personal_ride = models.ForeignKey(PersonalRide, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    seat_booking = models.ForeignKey(SeatBooking, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.amount} so'm ({self.status})"
