from rest_framework.generics import CreateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserRegistrationSerializer,PackageSerializer,BookingSerializer,PackageImageSerializer,ContactQuerySerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Packages,BookingTour,PackageImage,CustomUser
from rest_framework.views import APIView
from .utils import notify_admin,notify_user,is_agent,is_owner
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError

class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#user package view

class PackagesListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if self.request.user.role != CustomUser.Roles.USER:
            return Response({"error": "Only user can access."}, status=status.HTTP_403_FORBIDDEN)
        package = Packages.objects.filter(is_approved=True)
        serializer = PackageSerializer(package, many=True)
        return Response(serializer.data)
    
# # agent package creation and list ..

class PackageCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request,):
        user = request.user
        agent_check = is_agent(user)
        if agent_check:
            return agent_check

        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#agent update packages ...

class PackageUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        agent_check = is_agent(user)
        if agent_check:
            return agent_check
        packages = Packages.objects.filter(owner=user)
        serializer = PackageSerializer(packages, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        return self.update(request, pk, partial=True)

    def put(self, request, pk):
        return self.update(request, pk, partial=False)

    def update(self, request, pk, partial):
        user = request.user
        agent_check = is_agent(user)
        if agent_check:
            return agent_check
        try:
            package = Packages.objects.get(pk=pk)
        except Packages.DoesNotExist:
            return Response({"error": "Package not found."}, status=status.HTTP_404_NOT_FOUND)
        owner_check = is_owner(user, package)
        if owner_check:
            return owner_check
        serializer = PackageSerializer(package, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = request.user
        agent_check = is_agent(user)
        if agent_check:
            return agent_check
        try:
            package = Packages.objects.get(pk=pk)
        except Packages.DoesNotExist:
            return Response({"error": "Package not found."}, status=status.HTTP_404_NOT_FOUND)
        owner_check = is_owner(user, package)
        if owner_check:
            return owner_check
        package.delete()
        return Response({"message": "Package deleted successfully."}, status=status.HTTP_200_OK)



# agent image uploaded
    
class PackageImageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classe = [IsAuthenticated]

    def post(self, request):
        user = request.user

        agent_check = is_agent(user)
        if agent_check:
            return agent_check
        package_id = request.data.get('tour_package')
        try:
            package = Packages.objects.get(id=package_id, owner=user)
        except Packages.DoesNotExist:
            return Response({'error': 'Package not found or you are not the owner.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PackageImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, id):
        user = request.user
        agent_check = is_agent(user)
        if agent_check:
            return agent_check
        package_id = request.data.get('tour_package')
        try:
            package = Packages.objects.get(id=package_id, owner=user)
        except Packages.DoesNotExist:
            return Response({'error': 'Package not found or you are not the owner.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            image = PackageImage.objects.get(id=id, tour_package=package)
            image.delete()
            return Response({'message': 'Package image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except PackageImage.DoesNotExist:
            return Response({'error': 'Package image not found'}, status=status.HTTP_404_NOT_FOUND)

    
class BookingCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classe = [IsAuthenticated]

    def post(self,request):
        try:
            serializer = BookingSerializer(data=request.data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                booking = serializer.save()
                package = booking.package

                details = {
                    "title":package.name,
                    "number_of_people":package.number_of_people,
                    "travel_date":package.travel_date,
                 }
                
                notify_admin("Booking",details,user_email=request.user.email)
                notify_user("Booking",details,user_email=request.user.email)

                return Response({
                    "message": "Booking created successfully.",
                    "booking_id": booking.id,
                    "package_name": package.name,
                    "travel_date": booking.travel_date,
                    "number_of_people": booking.number_of_people,
                }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, id):
        try:
            booking = BookingTour.objects.get(id=id, user=request.user)
            if request.user != booking.user:
                return Response({'error': 'You are not authorized to delete this booking'}, status=status.HTTP_403_FORBIDDEN)

            booking.delete()
            return Response({'message': 'Booking deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except BookingTour.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)


class ContactQueryView(APIView):
    def post(self,request):
        serializer = ContactQuerySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message":"your query has been submitted successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    