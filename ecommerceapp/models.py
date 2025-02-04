
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    class Roles(models.IntegerChoices):
        AGENT = 1, "Agent"
        USER = 2, "User"
        ADMIN= 3,"Admin"

    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15,null=True,blank=True,validators=[RegexValidator( regex=r'^\+?1?\d{9,15}$', 
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",  )
        ],)
    address = models.TextField(null=True,blank=True) 
    role = models.IntegerField(choices=Roles.choices, default=Roles.USER) 
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    

class Packages(models.Model):
    owner =  models.ForeignKey(CustomUser, related_name="packages", on_delete=models.CASCADE)
    name =  models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.IntegerField()
    destination = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)

    # class Meta:
    #     verbrose_name = 'Package'
    #     verbrose_prural = 'Packages'
    
    def __str__(self):
        return self.name
    
    
class BookingTour(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    package =  models.ForeignKey(Packages,on_delete=models.CASCADE)
    number_of_people = models.PositiveIntegerField()
    amount = models.IntegerField()
    status = models.CharField(max_length=50,choices=[('pending','Pending'),('failed','Failed'),('cancel','Cancel'),('completed','Completed')],default='pending')
    travel_date = models.DateField()
    book_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.email} for {self.package.name}"
    
    
class Payment(models.Model):
    booking = models.ForeignKey(BookingTour,on_delete=models.CASCADE)
    status = models.CharField(max_length=150,choices=[('pending','Pending'),('completed','Completed'),('failed','Failed')],default='pending')
    amount = models.IntegerField()
    transaction_id = models.CharField(max_length=150,null=True,blank=True)
    created_date =models.DateTimeField(auto_now_add=True)
    checkout_id = models.CharField(max_length=300,default='stripe',unique=True)

    def __str__(self):
        return f"Payment for Booking {self.booking.id} - {self.status}"
    

class PackageImage(models.Model):
    tour_package = models.ForeignKey(Packages, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tour_packages/')
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.tour_package.name} - {self.id}"
    
    
class ContactQuery(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=100)
    messages = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


