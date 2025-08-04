#!/usr/bin/env python3
"""
Script para probar el backend de DUO Previa
"""
import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

class BackendTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health(self):
        """Test health endpoint"""
        print(" Testing health endpoint...")
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_login(self):
        """Test authentication"""
        print(" Testing authentication...")
        try:
            login_data = {
                "username": "admin",
                "password": "admin123",
                "restaurant_slug": "duo-previa"
            }
            
            async with self.session.post(
                f"{BASE_URL}/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    print(f"✅ Login successful for user: {data['user']['username']}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Login failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    async def test_get_restaurant(self):
        """Test get restaurant by slug"""
        print(" Testing get restaurant...")
        try:
            async with self.session.get(
                f"{BASE_URL}/api/restaurants/duo-previa"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Restaurant retrieved: {data['name']}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Get restaurant failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Get restaurant error: {e}")
            return False
    
    async def test_get_categories(self):
        """Test get categories"""
        print(" Testing get categories...")
        try:
            async with self.session.get(
                f"{BASE_URL}/api/duo-previa/categories"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Categories retrieved: {len(data)} categories")
                    for cat in data[:3]:  # Show first 3
                        print(f"   - {cat['name']}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Get categories failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Get categories error: {e}")
            return False
    
    async def test_get_products(self):
        """Test get products"""
        print(" Testing get products...")
        try:
            async with self.session.get(
                f"{BASE_URL}/api/duo-previa/products"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Products retrieved: {len(data)} products")
                    for prod in data[:3]:  # Show first 3
                        print(f"   - {prod['name']}: ${prod['price']}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Get products failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Get products error: {e}")
            return False
    
    async def test_create_order(self):
        """Test create order"""
        print(" Testing create order...")
        try:
            order_data = {
                "customer": {
                    "name": "Juan Pérez",
                    "phone": "+54 351 123-4567",
                    "email": "juan@example.com",
                    "address": "Av. Colón 456, Centro, Córdoba",
                    "delivery_notes": "Timbre B"
                },
                "items": [
                    {
                        "product_id": "test-product-1",
                        "product_name": "Lomito Completo",
                        "quantity": 2,
                        "unit_price": 4500.0,
                        "total_price": 9000.0
                    }
                ],
                "payment_method": "whatsapp",
                "is_delivery": True,
                "notes": "Sin cebolla"
            }
            
            async with self.session.post(
                f"{BASE_URL}/api/duo-previa/orders",
                json=order_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Order created: {data['order_number']}")
                    print(f"   Total: ${data['total']}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Create order failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Create order error: {e}")
            return False
    
    async def test_protected_endpoints(self):
        """Test protected endpoints"""
        if not self.auth_token:
            print("❌ No auth token available for protected endpoints")
            return False
            
        print(" Testing protected endpoints...")
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Test get orders
            async with self.session.get(
                f"{BASE_URL}/api/duo-previa/orders",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Orders retrieved: {len(data)} orders")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Get orders failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Protected endpoints error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print(" Starting DUO Previa Backend Tests")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health),
            ("Get Restaurant", self.test_get_restaurant),
            ("Get Categories", self.test_get_categories),
            ("Get Products", self.test_get_products),
            ("Create Order", self.test_create_order),
            ("Authentication", self.test_login),
            ("Protected Endpoints", self.test_protected_endpoints),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            result = await test_func()
            results.append((test_name, result))
        
        print("\n" + "=" * 50)
        print(" Test Results Summary:")
        print("=" * 50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<20} {status}")
            if result:
                passed += 1
        
        print(f"\nTotal: {passed}/{len(tests)} tests passed")
        
        if passed == len(tests):
            print("\n All tests passed! Backend is working correctly.")
        else:
            print(f"\n⚠️  {len(tests) - passed} tests failed. Check the logs above.")
        
        return passed == len(tests)

async def main():
    async with BackendTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    print("DUO Previa Backend Tester")
    print("Make sure the backend is running on http://localhost:8000")
    print("You can start it with: uvicorn main:app --reload\n")
    
    asyncio.run(main())
