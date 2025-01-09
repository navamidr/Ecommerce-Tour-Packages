from rest_framework.generics import CreateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserRegistrationSerializer,PackageSerializer,BookingSerializer,PackageImageSerializer
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

class PackageListCreateView(ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classe = [IsAuthenticated]
    queryset = Packages.objects.all()
    serializer_class = PackageSerializer

class PackageRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Packages.objects.all()
    serializer_class = PackageSerializer




class BookingCreate(APIView):
    def post(self,request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            package = validated_data['package'].id
            num_people = validated_data['number_of_people']
            travel_date = validated_data['travel_date']

            try:
                package = Packages.objects.get(id=package)

                if not package.is_approved:
                    return Response({"error": "Selected package is not approved."}, status=status.HTTP_400_BAD_REQUEST)
            
                booking = BookingTour.objects.create(
                    user=request.user,  
                    package=package,    
                    number_of_people=num_people,
                    travel_date=travel_date
                )
                subject = f"New Booking: {package.name}"
                message = (
                    f"A new booking has been made by {request.user.username}.\n\n"
                    f"Details:\n"
                    f"Package: {package.name}\n"
                    f"Number of People: {num_people}\n"
                    f"Travel Dates: {travel_date}\n"
                )
                admin_email = ["admin_email@example.com"]
                send_mail(subject, message, admin_email)

            
                user_subject = "Booking Confirmation"
                user_message = (
                    f"Thank you for booking {package.name}.\n\n"
                    f"Booking Details:\n"
                    f"Number of People: {num_people}\n"
                    f"Travel Dates: {travel_date}\n"
                )
                send_mail(user_subject, user_message, [request.user.email])

                return Response({
                    "message": "Booking created successfully.",
                    "booking_id": booking.id,
                    "package_name": package.name,
                    "travel_date": booking.travel_date,
                    "number_of_people": booking.number_of_people,
                }, status=status.HTTP_201_CREATED)
            
            except Packages.DoesNotExist:
                return Response({"error": "Package not found."}, status=status.HTTP_404_NOT_FOUND)

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





