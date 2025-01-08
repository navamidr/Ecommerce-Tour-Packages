from django.contrib import admin

# Register your models here.
from .models import Packages,BookingTour,Payment,ContactQuery


admin.site.register(Packages)
admin.site.register(BookingTour)
admin.site.register(Payment)
admin.site.register(ContactQuery)


class PackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'destination', 'price', 'is_approved']
    list_filter = ['is_approved']

admin.site.register(Packages,PackageAdmin)