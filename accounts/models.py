from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('passenger', 'Yo\'lovchi'),
        ('driver', 'Haydovchi'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='passenger')
    phone = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class DriverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_plate = models.CharField(max_length=20)
    car_model = models.CharField(max_length=100)
    car_color = models.CharField(max_length=50)
    total_seats = models.PositiveIntegerField(default=4)
    rating = models.FloatField(default=5.0)
    is_available = models.BooleanField(default=True)
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.car_model} ({self.license_plate})"
