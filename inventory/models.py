
from django.db import models
from django.core.validators import MinValueValidator
import django.db.models as models

class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('KG', 'Kilogram'),
        ('G', 'Gram'),
        ('L', 'Liter'),
        ('ML', 'Milliliter'),
        ('PC', 'Piece'),
        ('BTL', 'Bottle'),
        ('PKT', 'Packet'),
    ]

    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(max_length=200, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.quantity} {self.unit}"

    @property
    def is_in_stock(self):
        return self.quantity > 0

    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJ', 'Adjustment'),
        ('RET', 'Return'),
    ]

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.ingredient.name} - {self.quantity}"