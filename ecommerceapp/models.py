
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15,null=True,blank=True,validators=[RegexValidator( regex=r'^\+?1?\d{9,15}$', 
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",  )
        ],)
    address = models.TextField(null=True,blank=True)
    
    def __str__(self):
        return self.username

class Packages(models.Model):
    name =  models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    destination = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
class BookingTour(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    package =  models.ForeignKey(Packages,on_delete=models.CASCADE)
    number_of_people = models.PositiveIntegerField()
    travel_date = models.DateField()
    book_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.email} for {self.package.name}"

