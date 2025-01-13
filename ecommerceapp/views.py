from rest_framework.generics import CreateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserRegistrationSerializer,PackageSerializer,BookingSerializer,PackageImageSerializer,ContactQuerySerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Packages,BookingTour
from rest_framework.views import APIView
from django.core.mail import send_mail

class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# agent image uploaded
    
class PackageImageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classe = [IsAuthenticated]

    def post(self,request):
        if not request.user.is_agent:
            return Response({'error': 'Not an agent'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PackageImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#user package view

class PackagesListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        package = Packages.objects.filter(is_approved=True)
        serializer = PackageSerializer(package, many=True)
        return Response(serializer.data)
    
# agent package creation and list ..

class PackageCreateView(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classe = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class PackageRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classe = [IsAuthenticated]
    queryset = Packages.objects.all()
    serializer_class = PackageSerializer
    def perform_update(self, serializer):
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    def perform_destroy(self, instance):
        instance.delete()
        return Response({"message":"Deleted Package"})
    

class BookingCreate(APIView):
    def post(self,request):
        serializer = BookingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            booking = serializer.save()
            package = booking.package
            subject = f"New Booking: {package.name}"
            admin_message = (
                f"A new booking has been made by {request.user.username}.\n\n"
                f"Details:\n"
                f"Package: {package.name}\n"
                f"Number of People: {booking.number_of_people}\n"
                f"Travel Dates: {booking.travel_date}\n"
            )
            admin_email = ["admin_email@example.com"]
            send_mail(subject, admin_message, admin_email)
            user_message = (
                f"Thank you for booking {package.name}.\n\n"
                f"Booking Details:\n"
                f"Number of People: {booking.number_of_people}\n"
                f"Travel Dates: {booking.travel_date}\n"
            )
            send_mail("Booking Confirmation", user_message, [request.user.email])

            return Response({
                "message": "Booking created successfully.",
                "booking_id": booking.id,
                "package_name": package.name,
                "travel_date": booking.travel_date,
                "number_of_people": booking.number_of_people,
            }, status=status.HTTP_201_CREATED)


class ContcatQueryView(APIView):
    def post(self,request):
        serializer = ContactQuerySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message":"your query has been submitted successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    