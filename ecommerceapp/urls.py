from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)
from .views import UserRegistrationView,PackagesListView,PackageCreateView,PackageUpdateView,BookingCreate,PaymentView,CustomTokenObtainPairView,ContactQueryView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-btain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('packageslist/',PackagesListView.as_view(),name= 'packages-list'),
    path('packages/create/',PackageCreateView.as_view(),name='package-create'),
    path('packages/',PackageUpdateView.as_view(),name = 'package-retrieve-update-destroy'),
    path('packages/<int:id>/',PackageUpdateView.as_view(),name = 'package-retrieve-update-destroy'),
    path('bookingcreate/',BookingCreate.as_view(),name='booking-create'),
    path('bookingcreate/<int:id>/',BookingCreate.as_view(),name='booking-create'),
    path('bookings/user/<int:user_id>/', BookingCreate.as_view(), name='user-bookings'),

    path('create-checkout-session/', PaymentView.as_view(), name='create_checkout_session'),
    path('contactquery/',ContactQueryView.as_view(), name='Contact-query')

]
