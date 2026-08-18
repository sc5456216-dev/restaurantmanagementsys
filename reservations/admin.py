
from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'table', 'reservation_time', 'number_of_guests', 'status']
    list_filter = ['status', 'reservation_time']
    search_fields = ['customer_name', 'customer_phone', 'customer_email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Reservation Details', {
            'fields': ('table', 'number_of_guests', 'reservation_time', 'reservation_end_time')
        }),
        ('Status & Notes', {
            'fields': ('status', 'special_requests', 'created_by')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )