
from django.contrib import admin
from .models import Ingredient, InventoryTransaction

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit', 'reorder_level', 'is_in_stock', 'is_low_stock']
    list_filter = ['unit']
    search_fields = ['name', 'supplier']
    readonly_fields = ['last_updated', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'unit', 'supplier')
        }),
        ('Stock Information', {
            'fields': ('quantity', 'reorder_level', 'unit_price')
        }),
        ('System Fields', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['ingredient', 'transaction_type', 'quantity', 'unit_price', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['ingredient__name', 'notes']
    readonly_fields = ['created_at']