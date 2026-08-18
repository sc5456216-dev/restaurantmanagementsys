
from django.db import models
from tables.models import Table
from django.contrib.auth.models import User

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
        ('COMPLETED', 'Completed'),
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    number_of_guests = models.IntegerField()
    reservation_time = models.DateTimeField()
    reservation_end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    special_requests = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reservations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation for {self.customer_name} - Table {self.table.table_number}"

    def save(self, *args, **kwargs):
        # Auto-set end time if not provided (default 2 hours)
        if not self.reservation_end_time:
            from django.utils import timezone
            self.reservation_end_time = self.reservation_time + timezone.timedelta(hours=2)
        super().save(*args, **kwargs)