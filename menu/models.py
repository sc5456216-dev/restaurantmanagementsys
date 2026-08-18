
from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('APP', 'Appetizer'),
        ('MAIN', 'Main Course'),
        ('DESS', 'Dessert'),
        ('BEV', 'Beverage'),
        ('SIDE', 'Side Dish'),
        ('SPEC', 'Special'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    is_available = models.BooleanField(default=True)
    preparation_time = models.IntegerField(help_text="Preparation time in minutes", default=15)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    ingredients = models.TextField(help_text="List of ingredients", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        # Check if all ingredients are in stock
        for ingredient_item in self.menuitemingredient_set.all():
            if not ingredient_item.ingredient.is_in_stock:
                return False
        return True

class MenuItemIngredient(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey('inventory.Ingredient', on_delete=models.CASCADE)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=[
        ('KG', 'Kilogram'),
        ('G', 'Gram'),
        ('L', 'Liter'),
        ('ML', 'Milliliter'),
        ('PC', 'Piece'),
        ('BTL', 'Bottle'),
        ('PKT', 'Packet'),
    ])

    class Meta:
        unique_together = ['menu_item', 'ingredient']

    def __str__(self):
        return f"{self.menu_item.name} - {self.ingredient.name} ({self.quantity_required} {self.unit})"