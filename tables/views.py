
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Table
from .serializers import TableSerializer
from reservations.models import Reservation

class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.filter(is_active=True)
    serializer_class = TableSerializer

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        table = self.get_object()
        date_from = request.query_params.get('from')
        date_to = request.query_params.get('to')
        
        if not date_from or not date_to:
            return Response(
                {'error': 'Please provide both "from" and "to" datetime parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime
            dt_from = datetime.fromisoformat(date_from)
            dt_to = datetime.fromisoformat(date_to)
        except ValueError:
            return Response(
                {'error': 'Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if table is available in the requested time slot
        is_available = table.is_available(dt_from, dt_to)
        
        # Get conflicting reservations if any
        conflicting_reservations = []
        if not is_available:
            conflicting = Reservation.objects.filter(
                table=table,
                status__in=['CONFIRMED', 'CHECKED_IN'],
                reservation_time__lt=dt_to,
                reservation_end_time__gt=dt_from
            )
            conflicting_reservations = [
                {
                    'customer': res.customer_name,
                    'time': res.reservation_time.isoformat(),
                    'end_time': res.reservation_end_time.isoformat()
                }
                for res in conflicting
            ]
        
        return Response({
            'table_id': table.id,
            'table_number': table.table_number,
            'capacity': table.capacity,
            'is_available': is_available,
            'conflicting_reservations': conflicting_reservations
        })

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        table = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(Table.STATUS_CHOICES):
            return Response(
                {'error': f'Invalid status. Choose from: {dict(Table.STATUS_CHOICES).keys()}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        table.status = new_status
        table.save()
        return Response({
            'status': 'Table status updated',
            'table_id': table.id,
            'new_status': table.status
        })

    @action(detail=False, methods=['get'])
    def available_tables(self, request):
        """Get all available tables"""
        available = Table.objects.filter(status='AVAILABLE')
        serializer = self.get_serializer(available, many=True)
        return Response(serializer.data)