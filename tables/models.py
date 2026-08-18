
from django.db import models

class Table(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('RESERVED', 'Reserved'),
        ('MAINTENANCE', 'Under Maintenance'),
    ]

    table_number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField()
    location = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.table_number} - Capacity: {self.capacity}"

    def is_available(self, datetime_from, datetime_to):
        """Check if table is available for a given time slot"""
        # Check reservations
        from reservations.models import Reservation
        overlapping_reservations = Reservation.objects.filter(
            table=self,
            status__in=['CONFIRMED', 'CHECKED_IN'],
            reservation_time__lt=datetime_to,
            reservation_end_time__gt=datetime_from
        )
        return not overlapping_reservations.exists() and self.status == 'AVAILABLE'