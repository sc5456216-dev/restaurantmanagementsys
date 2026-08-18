
import requests
import json
from datetime import datetime

BASE_URL = 'http://127.0.0.1:8001/api'

def test_api():
    print("\n" + "=" * 60)
    print("🧪 TESTING RESTAURANT MANAGEMENT SYSTEM API")
    print("=" * 60 + "\n")
    
    # Test 1: Get Categories
    print("📌 1. GET /categories/")
    try:
        response = requests.get(f'{BASE_URL}/categories/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} categories")
            for cat in data[:3]:
                print(f"   └─ {cat['name']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Test 2: Get Menu Items
    print("📌 2. GET /menu-items/")
    try:
        response = requests.get(f'{BASE_URL}/menu-items/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} menu items")
            for item in data[:3]:
                print(f"   └─ {item['name']}: ${item['price']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Test 3: Get Tables
    print("📌 3. GET /tables/")
    try:
        response = requests.get(f'{BASE_URL}/tables/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} tables")
            for table in data[:3]:
                print(f"   └─ Table {table['table_number']}: {table['status']} (Capacity: {table['capacity']})")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Test 4: Get Ingredients
    print("📌 4. GET /ingredients/")
    try:
        response = requests.get(f'{BASE_URL}/ingredients/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} ingredients")
            for ing in data[:3]:
                print(f"   └─ {ing['name']}: {ing['quantity']} {ing['unit']}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Test 5: Get Available Tables
    print("📌 5. GET /tables/available_tables/")
    try:
        response = requests.get(f'{BASE_URL}/tables/available_tables/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data)} available tables")
            for table in data[:3]:
                print(f"   └─ Table {table['table_number']} (Capacity: {table['capacity']})")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    # Test 6: Get Stock Alerts
    print("📌 6. GET /reports/stock_alerts/")
    try:
        response = requests.get(f'{BASE_URL}/reports/stock_alerts/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total alerts: {data.get('total_alerts', 0)}")
            if data.get('low_stock'):
                print(f"   Low stock items: {len(data['low_stock'])}")
            if data.get('out_of_stock'):
                print(f"   Out of stock items: {len(data['out_of_stock'])}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    print("=" * 60)
    print("✅ API TESTS COMPLETED!")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    test_api()