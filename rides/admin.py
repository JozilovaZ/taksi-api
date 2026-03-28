from django.contrib import admin
from .models import PersonalRide, CompanionTrip, SeatBooking, Payment

admin.site.register(PersonalRide)
admin.site.register(CompanionTrip)
admin.site.register(SeatBooking)
admin.site.register(Payment)
