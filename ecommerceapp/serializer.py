from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Packages,BookingTour,Payment,ContactQuery,PackageImage
from datetime import date
from django.core.exceptions import ValidationError
import re



User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.Roles.choices)  
    email = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'contact', 'address','role']

    def validate_role(self, value):
        if value not in [role[0] for role in User.Roles.choices]:
            raise serializers.ValidationError("Invalid role selected.")
        return value

    def validate_email(self, value):
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, value):
            raise ValidationError("Enter a valid email address.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Packages
        fields = ['id', 'name', 'description', 'amount', 'start_date', 'end_date', 'destination', 'is_approved']
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive value.")
        return value
    
    

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingTour
        fields = ['id', 'user', ' package', 'number_of_people', 'travel_date', 'book_date','status']

    def validate_package(self,package):
        if not package.is_approved:
            raise serializers.ValidationError("Selected package is not approved.")
        return package
    
    def validate_travel_date(self,travel_date):
        if travel_date < date.today():
            raise serializers.ValidationError("Travel date must be in the future.")
        return travel_date

    def validate_number_of_people(self,num_people):
        if num_people < 1:
            raise serializers.ValidationError("Number of people must be at least 1.")
        return num_people

    def create(self, validated_data):
        user = self.context['request'].user  
        return BookingTour.objects.create(user=user, **validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class PackageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageImage
        fields = ['id', 'tour_package', 'image', 'description']

    def validate_tour_package(self, value):
        if not value:
            raise serializers.ValidationError("Tour package is required.")
        return value
        

class ContactQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactQuery
        fields = ['name', 'email', 'contact', 'messages']