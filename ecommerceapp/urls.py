from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)
from .views import UserRegistrationView,PackageImageView,PackagesListView,PackageCreateView,PackageUpdateView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token-btain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('packageslist/',PackagesListView.as_view(),name= 'packages-list'),
    path('packages/create/',PackageCreateView.as_view(),name='package-create'),
    path('packageimage/',PackageImageView.as_view(),name='package-image'),
    path('packages/',PackageUpdateView.as_view(),name = 'package-retrieve-update-destroy'),
    path('packages/<int:pk>/',PackageUpdateView.as_view(),name = 'package-retrieve-update-destroy'),

]
