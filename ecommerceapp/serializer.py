from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Packages,BookingTour,Payment,ContactQuery,PackageImage
from datetime import date
from django.core.exceptions import ValidationError
import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



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
        
        if User.objects.filter(email=value).exists():
            raise ValidationError("This email address is already registered.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        return {**super().validate(attrs), "message": "login successful."}
    
    
class PackageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageImage
        fields = ['id', 'tour_package', 'image', 'description']

    def validate_tour_package(self, value):
        if not value:
            raise serializers.ValidationError("Tour package is required.")
        return value
    

class PackageSerializer(serializers.ModelSerializer):
    images = PackageImageSerializer(many=True, read_only=True, source='packageimage_set')

    class Meta:
        model = Packages
        fields = ['id', 'name', 'description', 'amount', 'start_date', 'end_date', 'destination', 'is_approved','images']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive value.")
        return value

    def validate_start_date(self,start_date):
        if start_date < date.today():
            raise serializers.ValidationError("Travel date must be in the future.")
        return start_date
    
    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({'end_date': "End date must be after the start date."})
        return attrs
    
    def create(self, validated_data):
        request = self.context['request']
        images = request.FILES.getlist('images')  # Fetch all uploaded files with key 'images'
        descriptions = request.data.getlist('images.description', [])

        package = Packages.objects.create(owner=request.user, **validated_data)

                # Save associated images
        for image, description in zip(images, descriptions):
            PackageImage.objects.create(
                tour_package=package,
                image=image,
                description=description,
            )
        return package


class BookingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BookingTour
        fields = ['id', 'package','number_of_people', 'travel_date', 'book_date','status']

    def validate_package(self,package):
        if not package.is_approved:
            raise serializers.ValidationError("Selected package is not approved.")
        return package
    
    def validate_travel_date(self,travel_date):
        if travel_date < date.today():
            raise serializers.ValidationError("Travel date must be in the future.")
        return travel_date
    
    def validate(self, attrs):
        package = attrs.get('package')
        travel_date = attrs.get('travel_date')
        if package and travel_date:
            if travel_date < package.start_date:
                raise serializers.ValidationError({'travel_date': f"Travel date must not be before the package's start date ({package.start_date})."})
            if travel_date > package.end_date:
                raise serializers.ValidationError({'travel_date': f"Travel date must not be after the package's end date ({package.end_date})."})
        return attrs

    def validate_number_of_people(self,num_of_people):
        if num_of_people < 1:
            raise serializers.ValidationError("Number of people must be at least 1.")
        return num_of_people

    def create(self, validated_data):
        user = self.context['request'].user  
        package = validated_data['package']
        number_of_people = validated_data['number_of_people']
        amount = package.amount * number_of_people
        return BookingTour.objects.create(
            user=user,
            package=package,
            number_of_people=number_of_people,
            travel_date=validated_data['travel_date'],
            status=validated_data['status'],
            amount=amount
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'status', 'amount', 'transaction_id', 'created_date', 'checkout_id']
        read_only_fields = ['id', 'created_date', 'status', 'transaction_id']  

    def validate_booking(self, booking):
        if booking.payment_set.filter(status='completed').exists():
            raise serializers.ValidationError("Payment for this booking has already been completed.")
        return booking
    
    def validate_transaction_id(self, transaction_id):
        if Payment.objects.filter(transaction_id=transaction_id).exists():
            raise serializers.ValidationError("Transaction ID must be unique.")
        return transaction_id
    
    def create(self, validated_data):
        booking = validated_data['booking']
        validated_data['amount'] = booking.amount 
        return Payment.objects.create(**validated_data)
        

class ContactQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactQuery
        fields = ['name', 'email', 'contact', 'messages']

    def validate_email(self, value):
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, value):
            raise ValidationError("Enter a valid email address.")
        return value
    
    def validate_contact(self, value):
        if not re.fullmatch(r"^\d{10}$", value): 
            raise serializers.ValidationError("Contact must be a 10-digit number.")
        return value
    
    def validate_messages(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message should be at least 10 characters long.")
        return value
    
    def create(self, validated_data):
        return ContactQuery.objects.create(**validated_data)
    

