from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Packages,BookingTour,Payment,ContactQuery,PackageImage


User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'contact', 'address','is_agent']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packages
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingTour
        fields = ['id', 'user', ' package', 'number_of_people', 'travel_date', 'book_date']

    def validate_package(self,package):
        if not package.is_approved:
            raise serializers.ValidationError("Selected package is not approved.")
        return package
    
    def create(self, validated_data):
        user = self.context['request'].user  # Get the current authenticated user
        return BookingTour.objects.create(user=user, **validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PackageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageImage
        fields = ['id', 'tour_package', 'image', 'description']

class ContactQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactQuery
        fields = ['name', 'email', 'contact', 'messages']