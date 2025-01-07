from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Packages,BookingTour


User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'contact', 'address']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            contact=validated_data.get('contact', ''),
            address=validated_data.get('address', ''),
        )
        return user
    

class PackageSerializer(serializers.ModelSerializer):
    class Mata:
        model = Packages
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingTour
        fields = '__all__'
