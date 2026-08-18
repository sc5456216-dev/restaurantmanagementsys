
from rest_framework import serializers
from .models import Reservation
from tables.models import Table

class ReservationSerializer(serializers.ModelSerializer):
    table_number = serializers.CharField(source='table.table_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Reservation
        fields = ['id', 'table', 'table_number', 'customer_name', 'customer_phone', 
                 'customer_email', 'number_of_guests', 'reservation_time', 
                 'reservation_end_time', 'status', 'special_requests', 
                 'created_by', 'created_by_name', 'created_at', 'updated_at']

class ReservationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['table', 'customer_name', 'customer_phone', 'customer_email', 
                 'number_of_guests', 'reservation_time', 'reservation_end_time', 
                 'special_requests']
    
    def validate(self, data):
        table = data.get('table')
        reservation_time = data.get('reservation_time')
        reservation_end_time = data.get('reservation_end_time')
        
        # Check if table is available for the requested time
        if not table.is_available(reservation_time, reservation_end_time):
            raise serializers.ValidationError(
                "Table is not available for the requested time slot"
            )
        
        return data