from rest_framework.generics import CreateAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
import stripe
from django.utils.timezone import now
from .serializer import UserRegistrationSerializer,PackageSerializer,BookingSerializer,ContactQuerySerializer,PaymentSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Packages,BookingTour,PackageImage,CustomUser,Payment
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import notify_admin,notify_user
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from .permissions import IsAgent, IsOwner,IsUser
from .serializer import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.shortcuts import render,redirect
from django.http import Http404


stripe.api_key = settings.STRIPE_SECRET_KEY

# register view

class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully.","user":serializer.data}, status=status.HTTP_201_CREATED)
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
        today = now().date() 
        if search_query:
            packages = Packages.objects.filter(is_approved=True,name__icontains=search_query)
        else:
            packages = Packages.objects.filter(is_approved=True,start_date__gt=today)
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
            
            package_details = {
                "title": package.name,
                "Description": package.description,
                "Amount": package.amount,
                "Created By": request.user.email,
            }

            notify_admin("Package Creation", details=package_details, user_email=request.user.email)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
            
            # Notify admin on package update
            details = {
                "title": f"Package '{package.name}' Updated",
                "Destination": package.destination,
                "Amount": package.amount,
                "Updated By": request.user.email,
            }
            notify_admin("Package Update", details, request.user.email)

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
            # Notify admin on image deletion
            details = {
                "title": f"Image Deletion for Package '{image.tour_package.name}'",
                "Description": image.description,
                "Deleted By": request.user.email,
            }
            notify_admin("Image Deletion", details, request.user.email)

            return Response({"message": "Image deleted successfully."}, status=status.HTTP_200_OK)
        try:
            package = Packages.objects.get(id=id)
        except Packages.DoesNotExist:
            return Response({"error": "Package not found."}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, package)  
        package.delete()

        # Notify admin on package deletion
        details = {
            "title": f"Package '{package.name}' Deleted",
            "Deleted By": request.user.email,
        }
        notify_admin("Package Deletion", details, request.user.email)
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
                    "number of people":booking.number_of_people,
                    "travel date":booking.travel_date,
                 }
                
                notify_admin("Booking Successfully", details,user_email=request.user.email)
                notify_user("Booking Successfully", details,user_email=request.user.email)

                return Response({
                    "message": "Booking created successfully.",
                    "booking_id": booking.id,
                    "package_name": package.name,
                    "travel_date": booking.travel_date,
                    "number_of_people": booking.number_of_people,
                    "amount": booking.amount, 
                    "status":booking.status,
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
                return Response({'error': 'You are not authorized to cancel this booking'}, status=status.HTTP_403_FORBIDDEN)
             
            if booking.status == 'canceled':
                return Response({'error': 'This booking is already canceled'}, status=status.HTTP_400_BAD_REQUEST)

            # Update the status to "canceled" instead of deleting
            booking.status = 'canceled'
            booking.save()
            return Response({'message': 'Booking cancel successfully'}, status=status.HTTP_204_NO_CONTENT)
        except BookingTour.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
 
# payment view 

class CreateCheckoutSessionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,IsUser]

    def post(self, request):
        booking_id = request.data.get("booking_id")  # Fetch booking_id from the request body
        if not booking_id:
            return Response({"error": "Booking ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the booking object
            booking = BookingTour.objects.get(id=booking_id, user=request.user)  # Ensure user owns the booking
            
            # Check if booking status is canceled
            if booking.status == 'canceled':
                return Response(
                    {"error": f"Booking '{booking.package.name}' has been canceled and cannot proceed to payment."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            existing_payment = Payment.objects.filter(booking=booking, status='completed').first()
            if existing_payment:
                return Response(
                    {"error": f"Payment for booking {booking.package.name} has already been completed."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calculate amount in cents
            amount = int(booking.amount) * 100  # Convert to cents for Stripe

            # Create Stripe Checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "inr",
                        "product_data": {"name": f"Booking for {booking.package.name}"},
                        "unit_amount": amount,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=f"{settings.YOUR_DOMAIN}/api/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.YOUR_DOMAIN}/api/payment-cancel",
            )

            # Save payment details in the database
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.amount,
                status="pending",
                checkout_id=session.id,
            )

            # Respond with Stripe session details
            return Response({
                "message": "Stripe Checkout session created successfully.",
                "session_id": session.id,
                "url": session.url,
                "payment_id": payment.id,
            }, status=status.HTTP_201_CREATED)

        except BookingTour.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.GET.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is missing'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Retrieve the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)

            # Find the associated Payment record
            payment = Payment.objects.get(checkout_id=session_id)

            # Update payment status based on Stripe's response
            if session.payment_status == 'paid':
                payment.status = 'completed'
                payment.transaction_id = session.payment_intent  # Set the transaction ID from Stripe's session
                payment.save()

                booking = payment.booking
                booking.status = 'completed'
                booking.save()

                payment_details = {
                    "title": payment.booking.package.name,
                    "Transaction ID": payment.transaction_id,
                    "Amount": payment.amount,
                    "Status": payment.status,
                    "Booking": str(payment.booking),
                }

                # Notify admin and user
                notify_admin(notification_type="Payment Successfully", details=payment_details, user_email=payment.booking.user.email)
                notify_user(notification_type="Payment Successfully", details=payment_details, user_email=payment.booking.user.email)

                # return redirect(f"/api/success/{payment.id}/")

                return Response({
                    "message": "Payment successful!",
                    "payment_id": payment.id,
                    "transaction_id": payment.transaction_id,  # Include transaction ID in the response
                    "amount": payment.amount,
                    "payment_status": session.payment_status,
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Payment not completed'}, status=status.HTTP_400_BAD_REQUEST)

        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SuccessPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, payment_id):
        try:
            # Fetch the payment details by ID
            payment = Payment.objects.get(id=payment_id)
        
            # Pass payment, booking, and other relevant details to the template
            context = {
                'payment': payment,
                'booking': payment.booking,
                'package': payment.booking.package,
                'user': payment.booking.user,
            }
            return render(request, 'success.html', context)
        except Payment.DoesNotExist:
            raise Http404("Payment not found")


class PaymentCancelView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.GET.get('session_id')

        if not session_id:
            return Response({'error': 'Session ID is missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the payment using the session_id
            payment = Payment.objects.get(checkout_id=session_id)
            payment.status = 'failed'
            payment.save() 

            booking = payment.booking
            booking.status = 'failed'
            booking.save()

            payment_details = {
                "title": payment.booking.package.name,
                "Booking": str(payment.booking),
            }

                # Notify admin and user
            notify_admin(notification_type="Payment Cancel", details=payment_details, user_email=payment.booking.user.email)
            notify_user(notification_type="Payment Cancel", details=payment_details, user_email=payment.booking.user.email)

            # return redirect(f"/api/cancel/{payment.id}/")

            return Response({
                'message': 'Payment was canceled.',
                "payment_id":payment.id,
                "amount":payment.amount,
                }, status=status.HTTP_200_OK)

        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CancelPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, payment_id):
        try:
            # Fetch the payment details by ID
            payment = Payment.objects.get(id=payment_id)
        
            # Pass payment, booking, and other relevant details to the template
            context = {
                'payment': payment,
                'booking': payment.booking,
                'package': payment.booking.package,
                'user': payment.booking.user,
            }
            return render(request, 'cancel.html', context)
        except Payment.DoesNotExist:
            raise Http404("Payment not found")


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
    