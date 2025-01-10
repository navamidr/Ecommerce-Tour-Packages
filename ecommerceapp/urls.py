from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)
from .views import UserRegistrationView,PackageImageView,PackagesListView,PackageCreateView,PackageRetrieveUpdateDestroyView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('packageimage',PackageImageView.as_view(),name='packageimage'),
    path('packageslist/',PackagesListView.as_view(),name= 'packageslist'),
    path('packages/create/',PackageCreateView.as_view(),name='packagecreate'),
    path('packages/<int:pk>/',PackageRetrieveUpdateDestroyView.as_view(),name = 'packageretrieveupdatedestroy'),

]
