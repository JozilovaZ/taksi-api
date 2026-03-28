from django.urls import path
from . import views

urlpatterns = [
    # ── Shaxsiy rejim ──
    path('personal/create/', views.PersonalRideCreateView.as_view(), name='personal-ride-create'),
    path('personal/<int:pk>/', views.PersonalRideDetailView.as_view(), name='personal-ride-detail'),
    path('personal/my/', views.MyPersonalRidesView.as_view(), name='my-personal-rides'),
    path('personal/<int:pk>/accept/', views.accept_personal_ride, name='accept-personal-ride'),
    path('personal/<int:pk>/status/', views.update_ride_status, name='update-ride-status'),
    path('personal/available/', views.available_rides_for_driver, name='available-rides'),

    # ── Hamroh rejim ──
    path('companion/create/', views.CompanionTripCreateView.as_view(), name='companion-trip-create'),
    path('companion/', views.CompanionTripListView.as_view(), name='companion-trip-list'),
    path('companion/<int:pk>/', views.CompanionTripDetailView.as_view(), name='companion-trip-detail'),
    path('companion/<int:pk>/book/', views.book_seat, name='book-seat'),
    path('companion/<int:pk>/status/', views.update_trip_status, name='update-trip-status'),

    # ── Booking ──
    path('booking/<int:pk>/confirm/', views.confirm_booking, name='confirm-booking'),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel-booking'),

    # ── To'lovlar ──
    path('payments/', views.MyPaymentsView.as_view(), name='my-payments'),
]
