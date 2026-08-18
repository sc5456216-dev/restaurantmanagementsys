
from rest_framework import serializers
from .models import Ingredient, InventoryTransaction

class IngredientSerializer(serializers.ModelSerializer):
    is_in_stock = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'unit', 'quantity', 'reorder_level', 'unit_price', 
                 'supplier', 'is_in_stock', 'is_low_stock', 'last_updated', 'created_at']

class InventoryTransactionSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = ['id', 'ingredient', 'ingredient_name', 'transaction_type', 
                 'transaction_type_display', 'quantity', 'unit_price', 
                 'notes', 'created_by', 'created_at']