
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Reservation
from .serializers import ReservationSerializer, ReservationCreateSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all().order_by('-reservation_time')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReservationCreateSerializer
        return ReservationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check table availability
        table = serializer.validated_data['table']
        reservation_time = serializer.validated_data['reservation_time']
        reservation_end_time = serializer.validated_data.get('reservation_end_time')
        
        if not reservation_end_time:
            reservation_end_time = reservation_time + timezone.timedelta(hours=2)
        
        if not table.is_available(reservation_time, reservation_end_time):
            return Response(
                {'error': 'Table is not available for the requested time slot'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save reservation
        reservation = serializer.save(created_by=request.user if request.user else None)
        
        # Update table status to reserved
        table.status = 'RESERVED'
        table.save()
        
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        reservation = self.get_object()
        
        if reservation.status != 'CONFIRMED':
            return Response(
                {'error': f'Only confirmed reservations can be checked in. Current status: {reservation.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if table is still available
        if not reservation.table.is_available(
            reservation.reservation_time, 
            reservation.reservation_end_time
        ):
            return Response(
                {'error': 'Table is no longer available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update reservation and table status
        reservation.status = 'CHECKED_IN'
        reservation.table.status = 'OCCUPIED'
        reservation.table.save()
        reservation.save()
        
        return Response({
            'status': 'Check-in successful',
            'reservation': ReservationSerializer(reservation).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        
        if reservation.status in ['COMPLETED', 'NO_SHOW']:
            return Response(
                {'error': f'Cannot cancel a {reservation.status} reservation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.status = 'CANCELLED'
        reservation.save()
        
        # Free the table
        if reservation.table.status == 'RESERVED':
            reservation.table.status = 'AVAILABLE'
            reservation.table.save()
        
        return Response({
            'status': 'Reservation cancelled',
            'reservation_id': reservation.id
        })

    @action(detail=False, methods=['get'])
    def today_reservations(self, request):
        """Get today's reservations"""
        today = timezone.now().date()
        reservations = self.queryset.filter(
            reservation_time__date=today,
            status__in=['PENDING', 'CONFIRMED']
        )
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)