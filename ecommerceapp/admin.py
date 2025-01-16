from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# Register your models here.
from .models import CustomUser,Packages,BookingTour,Payment


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



class PackageAdmin(admin.ModelAdmin):
    list_display = ['owner','name', 'destination','is_approved']
    list_filter = ['is_approved']

admin.site.register(Packages,PackageAdmin)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'number_of_people', 'travel_date', 'book_date')
    search_fields = ('user__username', 'user__email', 'package__name')
    fieldsets = (
        ('User and Package Details', {
            'fields': ('user', 'package')
        }),
        ('Booking Details', {
            'fields': ('number_of_people', 'travel_date')
        }),
        ('Metadata', {
            'fields': ('book_date',),
            'classes': ('collapse',), 
        }),
    )
    readonly_fields = ('book_date',)

admin.site.register(BookingTour, BookingAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'amount', 'created_date')
    list_filter = ('status', 'created_date')
    search_fields = ('booking__id', 'booking__user__username', 'booking__package__name')
    readonly_fields = ('created_date',)
    
admin.site.register(Payment, PaymentAdmin)
