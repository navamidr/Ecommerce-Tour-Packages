from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)
from .views import UserRegistrationView,PackagesListView,PackageCreateView,PackageUpdateView,BookingCreate,CreateCheckoutSessionView, PaymentSuccessView,PaymentCancelView,CustomTokenObtainPairView,ContactQueryView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-btain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('packageslist/',PackagesListView.as_view(),name= 'packages-list'),
    path('packages/create/',PackageCreateView.as_view(),name='package-create'),
    path('packages/',PackageUpdateView.as_view(),name = 'package-retrieve-update-destroy'),
    path('packages/<int:id>/',PackageUpdateView.as_view(),name = 'package-retrieve-update-destroy'),
    path('bookingcreate/',BookingCreate.as_view(),name='booking-create'),
    path('bookingcreate/<int:id>/',BookingCreate.as_view(),name='booking-create'),
    path('bookings/user/<int:user_id>/', BookingCreate.as_view(), name='user-bookings'),
    path('create/checkoutsession/', CreateCheckoutSessionView.as_view(), name='create-checkout-ession'),
    path('payment-success/', PaymentSuccessView.as_view(),name='payment-success'),
    path('payment-cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('contactquery/',ContactQueryView.as_view(), name='contact-query')

]
