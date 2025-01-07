from rest_framework.generics import CreateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserRegistrationSerializer,PackageSerializer,BookingSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
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

class PackagesListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        package = Packages.objects.filter(is_approved=True)
        serializer = PackageSerializer(package, many=True)
        return Response(serializer.data)

class PackageListCreateView(ListCreateAPIView):
    queryset = Packages.objects.all()
    serializer_class = PackageSerializer

class PackageRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Packages.objects.all()
    serializer_class = PackageSerializer



class BookingCreate(APIView):
    def post(self,request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(user=request.user)
            send_mail(
                'New Booking Created',
                f'Booking Details: {booking.package.name}, {booking.number_of_people} people.',
                'admin@gmail.com',
                ['admin@gmail.com']
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

