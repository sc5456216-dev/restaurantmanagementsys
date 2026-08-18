
from django.contrib import admin
from .models import Category, MenuItem, MenuItemIngredient

class MenuItemIngredientInline(admin.TabularInline):
    model = MenuItemIngredient
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'is_available', 'created_at']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']
    inlines = [MenuItemIngredientInline]