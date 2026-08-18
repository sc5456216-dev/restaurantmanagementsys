
from rest_framework import serializers
from .models import Category, MenuItem, MenuItemIngredient

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class MenuItemIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    
    class Meta:
        model = MenuItemIngredient
        fields = ['id', 'ingredient', 'ingredient_name', 'quantity_required', 'unit']

class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    ingredients = MenuItemIngredientSerializer(source='menuitemingredient_set', many=True, read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'category', 'category_name', 
                 'is_available', 'preparation_time', 'image', 'ingredients', 'is_in_stock']

class MenuItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'is_available', 
                 'preparation_time', 'image', 'ingredients']