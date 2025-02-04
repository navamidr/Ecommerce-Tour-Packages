from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.
from .models import CustomUser,Packages,BookingTour,Payment,PackageImage,ContactQuery


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'contact', 'address','role']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role', 'contact', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'contact', 'address')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)


class PackageImageInline(admin.TabularInline): 
    model = PackageImage
    extra = 1  
    fields = ['image', 'description']  # Fields to display in the inline

# Customize the PackageAdmin
class PackageAdmin(admin.ModelAdmin):
    list_display = ['owner', 'name', 'destination', 'is_approved']
    list_filter = ['is_approved']
    inlines = [PackageImageInline]  # Include the inline model

admin.site.register(Packages, PackageAdmin)


class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'number_of_people', 'travel_date', 'book_date','status')
    search_fields = ('user__username', 'user__email', 'package__name')
    readonly_fields = ('book_date',)

admin.site.register(BookingTour, BookingAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'amount', 'transaction_id','created_date')
    list_filter = ('status', 'created_date')
    search_fields = ('booking__id', 'booking__user__username', 'booking__package__name')
    readonly_fields = ('created_date','transaction_id')
    
admin.site.register(Payment, PaymentAdmin)


class PackageImageAdmin(admin.ModelAdmin):
    list_display= ('tour_package','image','description')
admin.site.register(PackageImage,PackageImageAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name','email','contact','messages')
admin.site.register(ContactQuery,ContactAdmin)
