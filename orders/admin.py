
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'customer_name', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'id']
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_phone')
        }),
        ('Order Details', {
            'fields': ('table', 'status', 'total_amount', 'tax', 'discount', 'service_charge')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'menu_item', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['order__id', 'menu_item__name']