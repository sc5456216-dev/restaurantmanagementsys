
from rest_framework import serializers
from .models import Table

class TableSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'capacity', 'location', 'status', 
                 'status_display', 'is_active', 'created_at', 'updated_at']