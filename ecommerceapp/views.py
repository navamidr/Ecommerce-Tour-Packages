from rest_framework.generics import CreateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserRegistrationSerializer,PackageSerializer,BookingSerializer,ContactQuerySerializer,PaymentSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Packages,BookingTour,PackageImage,CustomUser
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import notify_admin,notify_user
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from .permissions import IsAgent, IsOwner,IsUser
from .serializer import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# register view

class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# login 

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

#user package view

class PackagesListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsUser]

    def get(self, request):
        search_query = request.query_params.get('search', '')
        if search_query:
            packages = Packages.objects.filter(is_approved=True,name__icontains=search_query)
        else:
            packages = Packages.objects.filter(is_approved=True)
        serializer = PackageSerializer(packages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# # agent package creation 

class PackageCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAgent]
    parser_classes = [MultiPartParser, FormParser]  # Allow handling file uploads

    def post(self, request):
        serializer = PackageSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            package = serializer.save()  # Save the Package instance
            # Save the associated images
            for key, file in request.FILES.items():
                if key.startswith("image"):
                    PackageImage.objects.create(
                        tour_package=package,
                        image=file,
                        description=f"Image for {package.name}"
                    )
            return Response(serializer.data, {"message":"New Package Created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PackageUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAgent, IsOwner]
    parser_classes = [MultiPartParser, FormParser]  # Allow handling file uploads

    def get(self, request):
        user = request.user
        packages = Packages.objects.filter(owner=user)
        if not packages.exists():
            return Response({"message": "No packages found for this user."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PackageSerializer(packages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id):
        try:
            package = Packages.objects.get(id=id)
        except Packages.DoesNotExist:
            return Response({"error": "Package not found."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, package)  
        serializer = PackageSerializer(package, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            package = serializer.save()
            # Update or add new images
            for key, file in request.FILES.items():
                if key.startswith("image"):
                    PackageImage.objects.create(
                        tour_package=package,
                        image=file,
                        description=f"Updated image for {package.name}"
                    )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        image_id = request.query_params.get('image_id', None)  

        if image_id:
            # Delete a specific image
            try:
                image = PackageImage.objects.get(pk=image_id, tour_package__owner=request.user)
            except PackageImage.DoesNotExist:
                return Response({"error": "Image not found or you don't have permission to delete it."}, status=status.HTTP_404_NOT_FOUND)

            image.delete()
            return Response({"message": "Image deleted successfully."}, status=status.HTTP_200_OK)
        try:
            package = Packages.objects.get(id=id)
        except Packages.DoesNotExist:
            return Response({"error": "Package not found."}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, package)  
        package.delete()
        return Response({"message": "Package deleted successfully."}, status=status.HTTP_200_OK)


# booking 
    
class BookingCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsUser]

    def post(self,request):
        try:
            serializer = BookingSerializer(data=request.data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                booking = serializer.save()
                package = booking.package

                details = {
                    "title":package.name,
                    "number_of_people":booking.number_of_people,
                    "travel_date":booking.travel_date,
                 }
                
                notify_admin("Booking", details,user_email=request.user.email)
                notify_user("Booking", details,user_email=request.user.email)

                return Response({
                    "message": "Booking created successfully.",
                    "booking_id": booking.id,
                    "package_name": package.name,
                    "travel_date": booking.travel_date,
                    "number_of_people": booking.number_of_people,
                    "amount": booking.amount, 
                }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, user_id):
        try:
            if user_id: 
                bookings = BookingTour.objects.filter(user__id=user_id)
                if not bookings.exists():
                    return Response({'error': 'No bookings found for this user'}, status=status.HTTP_404_NOT_FOUND)
                serializer = BookingSerializer(bookings, many=True, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            booking = BookingTour.objects.get(id=id, user=request.user)
            if request.user != booking.user:
                return Response({'error': 'You are not authorized to delete this booking'}, status=status.HTTP_403_FORBIDDEN)

            booking.delete()
            return Response({'message': 'Booking deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except BookingTour.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
 
# payment view 

class PaymentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsUser]

    def post(self,request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save() 
            
          #  payment functions
            return Response({
                "message": "Payment processed successfully.",
                "payment_id": payment.id,
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# contactquery view 

class ContactQueryView(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self,request):
        print(self.request.user)
        serializer = ContactQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"your query has been submitted successfully"}, status=status.HTTP_201_CREATED)
    