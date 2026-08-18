
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_backend.settings')
django.setup()

from django.contrib.auth.models import User
from menu.models import Category, MenuItem, MenuItemIngredient
from tables.models import Table
from inventory.models import Ingredient
from django.db import transaction

def populate_database():
    print("🚀 Starting to populate database...")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            # Create superuser if not exists
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
                print("✅ Superuser 'admin' created (password: admin123)")
            else:
                print("ℹ️  Superuser already exists")
            
            # Create categories
            categories_data = [
                {'name': 'Appetizers', 'description': 'Start your meal with these delicious options'},
                {'name': 'Main Course', 'description': 'Our signature main dishes'},
                {'name': 'Desserts', 'description': 'Sweet endings to your meal'},
                {'name': 'Beverages', 'description': 'Refreshing drinks'},
                {'name': 'Specials', 'description': "Chef's special creations"},
            ]
            
            categories = []
            for cat_data in categories_data:
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    defaults={'description': cat_data['description']}
                )
                categories.append(category)
                if created:
                    print(f"✅ Created category: {category.name}")
                else:
                    print(f"ℹ️  Category already exists: {category.name}")
            
            # Create ingredients
            ingredients_data = [
                {'name': 'Chicken Breast', 'unit': 'KG', 'quantity': 10.00, 'reorder_level': 2.00, 'unit_price': 5.99, 'supplier': 'Fresh Foods Inc.'},
                {'name': 'Tomatoes', 'unit': 'KG', 'quantity': 5.00, 'reorder_level': 1.00, 'unit_price': 2.99, 'supplier': 'Local Farms'},
                {'name': 'Onions', 'unit': 'KG', 'quantity': 5.00, 'reorder_level': 1.00, 'unit_price': 1.99, 'supplier': 'Local Farms'},
                {'name': 'Garlic', 'unit': 'KG', 'quantity': 2.00, 'reorder_level': 0.50, 'unit_price': 3.99, 'supplier': 'Local Farms'},
                {'name': 'Olive Oil', 'unit': 'L', 'quantity': 3.00, 'reorder_level': 1.00, 'unit_price': 8.99, 'supplier': 'Italian Imports'},
                {'name': 'Pasta', 'unit': 'KG', 'quantity': 8.00, 'reorder_level': 2.00, 'unit_price': 2.49, 'supplier': 'Italian Imports'},
                {'name': 'Cheese', 'unit': 'KG', 'quantity': 4.00, 'reorder_level': 1.00, 'unit_price': 6.99, 'supplier': 'Dairy Farms'},
                {'name': 'Flour', 'unit': 'KG', 'quantity': 6.00, 'reorder_level': 2.00, 'unit_price': 1.49, 'supplier': 'Local Farms'},
                {'name': 'Sugar', 'unit': 'KG', 'quantity': 5.00, 'reorder_level': 1.00, 'unit_price': 0.99, 'supplier': 'Local Farms'},
                {'name': 'Butter', 'unit': 'KG', 'quantity': 3.00, 'reorder_level': 0.50, 'unit_price': 4.99, 'supplier': 'Dairy Farms'},
            ]
            
            ingredients = []
            for ing_data in ingredients_data:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ing_data['name'],
                    defaults=ing_data
                )
                ingredients.append(ingredient)
                if created:
                    print(f"✅ Created ingredient: {ingredient.name}")
                else:
                    print(f"ℹ️  Ingredient already exists: {ingredient.name}")
            
            # Create tables
            tables_data = [
                {'table_number': 'T1', 'capacity': 2, 'location': 'Window', 'status': 'AVAILABLE'},
                {'table_number': 'T2', 'capacity': 4, 'location': 'Window', 'status': 'AVAILABLE'},
                {'table_number': 'T3', 'capacity': 4, 'location': 'Center', 'status': 'AVAILABLE'},
                {'table_number': 'T4', 'capacity': 6, 'location': 'Center', 'status': 'AVAILABLE'},
                {'table_number': 'T5', 'capacity': 8, 'location': 'Private Room', 'status': 'AVAILABLE'},
                {'table_number': 'T6', 'capacity': 2, 'location': 'Outdoor', 'status': 'AVAILABLE'},
                {'table_number': 'T7', 'capacity': 4, 'location': 'Outdoor', 'status': 'AVAILABLE'},
                {'table_number': 'T8', 'capacity': 6, 'location': 'Private Room', 'status': 'AVAILABLE'},
            ]
            
            for table_data in tables_data:
                table, created = Table.objects.get_or_create(
                    table_number=table_data['table_number'],
                    defaults=table_data
                )
                if created:
                    print(f"✅ Created table: {table.table_number} (Capacity: {table.capacity})")
                else:
                    print(f"ℹ️  Table already exists: {table.table_number}")
            
            # Create menu items with ingredient relationships
            menu_items_data = [
                {
                    'name': 'Grilled Chicken',
                    'description': 'Juicy grilled chicken breast with roasted vegetables and herbs',
                    'price': 18.99,
                    'category': categories[1],
                    'preparation_time': 20,
                    'ingredients': [
                        (ingredients[0], 0.20, 'KG'),
                        (ingredients[1], 0.10, 'KG'),
                        (ingredients[2], 0.05, 'KG'),
                        (ingredients[4], 0.02, 'L'),
                    ]
                },
                {
                    'name': 'Pasta Carbonara',
                    'description': 'Classic Italian pasta with creamy sauce and pancetta',
                    'price': 16.99,
                    'category': categories[1],
                    'preparation_time': 15,
                    'ingredients': [
                        (ingredients[5], 0.20, 'KG'),
                        (ingredients[6], 0.05, 'KG'),
                        (ingredients[2], 0.03, 'KG'),
                        (ingredients[3], 0.02, 'KG'),
                        (ingredients[4], 0.02, 'L'),
                    ]
                },
                {
                    'name': 'Caprese Salad',
                    'description': 'Fresh mozzarella, tomatoes, and basil with balsamic glaze',
                    'price': 12.99,
                    'category': categories[0],
                    'preparation_time': 10,
                    'ingredients': [
                        (ingredients[6], 0.10, 'KG'),
                        (ingredients[1], 0.15, 'KG'),
                        (ingredients[4], 0.01, 'L'),
                    ]
                },
                {
                    'name': 'Chocolate Cake',
                    'description': 'Rich chocolate cake with ganache frosting',
                    'price': 8.99,
                    'category': categories[2],
                    'preparation_time': 25,
                    'ingredients': [
                        (ingredients[7], 0.15, 'KG'),
                        (ingredients[8], 0.10, 'KG'),
                        (ingredients[9], 0.05, 'KG'),
                    ]
                },
                {
                    'name': 'Fresh Lemonade',
                    'description': 'Homemade lemonade with fresh lemons and mint',
                    'price': 4.99,
                    'category': categories[3],
                    'preparation_time': 5,
                    'ingredients': []
                },
                {
                    'name': 'Caesar Salad',
                    'description': 'Classic Caesar salad with crispy croutons and parmesan',
                    'price': 14.99,
                    'category': categories[0],
                    'preparation_time': 12,
                    'ingredients': [
                        (ingredients[6], 0.08, 'KG'),
                        (ingredients[1], 0.10, 'KG'),
                        (ingredients[4], 0.01, 'L'),
                    ]
                }
            ]
            
            for item_data in menu_items_data:
                menu_item, created = MenuItem.objects.get_or_create(
                    name=item_data['name'],
                    defaults={
                        'description': item_data['description'],
                        'price': item_data['price'],
                        'category': item_data['category'],
                        'preparation_time': item_data['preparation_time']
                    }
                )
                
                if created:
                    print(f"✅ Created menu item: {menu_item.name} (${menu_item.price})")
                    
                    for ingredient, quantity, unit in item_data['ingredients']:
                        MenuItemIngredient.objects.create(
                            menu_item=menu_item,
                            ingredient=ingredient,
                            quantity_required=quantity,
                            unit=unit
                        )
                        print(f"   └─ Added ingredient: {ingredient.name} - {quantity} {unit}")
                else:
                    print(f"ℹ️  Menu item already exists: {menu_item.name}")
            
            print("\n" + "=" * 50)
            print("🎉 DATABASE POPULATED SUCCESSFULLY!")
            print("=" * 50)
            print("\n📊 Summary:")
            print(f"   Categories: {Category.objects.count()}")
            print(f"   Menu Items: {MenuItem.objects.count()}")
            print(f"   Ingredients: {Ingredient.objects.count()}")
            print(f"   Tables: {Table.objects.count()}")
            print(f"   Users: {User.objects.count()}")
            
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        raise

if __name__ == '__main__':
    populate_database()