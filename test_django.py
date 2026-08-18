
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_backend.settings')
django.setup()

from django.test.client import Client
from django.urls import reverse
import json

def test_api():
    client = Client()
    
    print("\n" + "=" * 60)
    print("🧪 TESTING RESTAURANT MANAGEMENT SYSTEM API")
    print("=" * 60 + "\n")
    
    # Test 1: Get Categories
    print("📌 1. GET /api/categories/")
    response = client.get('/api/categories/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} categories")
        for cat in data[:3]:
            print(f"   └─ {cat['name']}")
    print()
    
    # Test 2: Get Menu Items
    print("📌 2. GET /api/menu-items/")
    response = client.get('/api/menu-items/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} menu items")
        for item in data[:3]:
            print(f"   └─ {item['name']}: ${item['price']}")
    print()
    
    # Test 3: Get Tables
    print("📌 3. GET /api/tables/")
    response = client.get('/api/tables/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} tables")
        for table in data[:3]:
            print(f"   └─ Table {table['table_number']}: {table['status']}")
    print()
    
    # Test 4: Get Ingredients
    print("📌 4. GET /api/ingredients/")
    response = client.get('/api/ingredients/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} ingredients")
        for ing in data[:3]:
            print(f"   └─ {ing['name']}: {ing['quantity']} {ing['unit']}")
    print()
    
    print("=" * 60)
    print("✅ API TESTS COMPLETED!")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    test_api()