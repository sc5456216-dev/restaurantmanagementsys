
from django.contrib import admin
from .models import Table

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_number', 'capacity', 'location', 'status', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['table_number', 'location']
    
    actions = ['mark_available', 'mark_occupied']
    
    def mark_available(self, request, queryset):
        queryset.update(status='AVAILABLE')
    mark_available.short_description = "Mark selected tables as Available"
    
    def mark_occupied(self, request, queryset):
        queryset.update(status='OCCUPIED')
    mark_occupied.short_description = "Mark selected tables as Occupied"