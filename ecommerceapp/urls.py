from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)
from .views import UserRegistrationView,PackageImageView,PackagesListView,PackageListCreateView,PackageRetrieveUpdateDestroyView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('packageimage',PackageImageView.as_view(),name='packageimage'),
    path('packageslist/',PackagesListView.as_view(),name= 'packageslist'),
    path('packagelistcreate',PackageListCreateView.as_view(),name='packagelistcreate'),
    path('packageretrieveupdatedestroy',PackageRetrieveUpdateDestroyView.as_view(),name = 'packageretrieveupdatedestroy'),

]
