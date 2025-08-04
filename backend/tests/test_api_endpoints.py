import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from main import app
from services.auth import AuthService

class TestAPIEndpoints:
    """Test suite for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock authentication service"""
        with patch('main.auth_service') as mock:
            yield mock
    
    @pytest.fixture
    def mock_restaurant_service(self):
        """Mock restaurant service"""
        with patch('main.restaurant_service') as mock:
            yield mock
    
    @pytest.fixture
    def mock_product_service(self):
        """Mock product service"""
        with patch('main.product_service') as mock:
            yield mock
    
    @pytest.fixture
    def mock_category_service(self):
        """Mock category service"""
        with patch('main.category_service') as mock:
            yield mock
    
    @pytest.fixture
    def mock_order_service(self):
        """Mock order service"""
        with patch('main.order_service') as mock:
            yield mock
    
    @pytest.fixture
    def valid_token(self):
        """Generate a valid test token"""
        auth_service = AuthService()
        return auth_service.create_access_token({
            "sub": "testuser",
            "restaurant_slug": "test-restaurant",
            "role": "admin",
            "user_id": "user_123"
        })
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        with patch('main.database') as mock_db:
            mock_db.database.command = AsyncMock()
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "version" in data
            assert "database" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
    
    def test_login_success(self, client, mock_auth_service):
        """Test successful login"""
        # Mock successful authentication
        mock_auth_service.authenticate_user = AsyncMock(return_value={
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": "user_123",
                "username": "testuser",
                "role": "admin",
                "restaurant_slug": "test-restaurant"
            }
        })
        
        response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass",
            "restaurant_slug": "test-restaurant"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "test_access_token"
        assert data["user"]["username"] == "testuser"
    
    def test_login_failure(self, client, mock_auth_service):
        """Test failed login"""
        # Mock failed authentication
        mock_auth_service.authenticate_user = AsyncMock(return_value=None)
        
        response = client.post("/auth/login", json={
            "username": "wronguser",
            "password": "wrongpass",
            "restaurant_slug": "test-restaurant"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
    
    def test_login_validation_error(self, client):
        """Test login with invalid data"""
        response = client.post("/auth/login", json={
            "username": "",  # Empty username
            "password": "pass"
            # Missing restaurant_slug
        })
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "errors" in data
    
    def test_refresh_token_success(self, client, mock_auth_service):
        """Test successful token refresh"""
        mock_auth_service.refresh_access_token = AsyncMock(return_value={
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": "user_123",
                "username": "testuser",
                "role": "admin",
                "restaurant_slug": "test-restaurant"
            }
        })
        
        response = client.post("/auth/refresh", json={
            "refresh_token": "valid_refresh_token"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new_access_token"
    
    def test_get_restaurant_success(self, client, mock_restaurant_service):
        """Test successful restaurant retrieval"""
        mock_restaurant_service.get_by_slug = AsyncMock(return_value={
            "id": "restaurant_123",
            "name": "Test Restaurant",
            "slug": "test-restaurant",
            "description": "A test restaurant",
            "logo": "",
            "phone": "+1234567890",
            "address": "123 Test St",
            "city": "Test City",
            "settings": {},
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        })
        
        response = client.get("/api/restaurants/test-restaurant")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Restaurant"
        assert data["slug"] == "test-restaurant"
    
    def test_get_restaurant_not_found(self, client, mock_restaurant_service):
        """Test restaurant not found"""
        mock_restaurant_service.get_by_slug = AsyncMock(return_value=None)
        
        response = client.get("/api/restaurants/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
    
    def test_get_categories(self, client, mock_category_service):
        """Test get categories endpoint"""
        mock_category_service.get_categories_by_restaurant = AsyncMock(return_value=[
            {
                "id": "cat_1",
                "name": "Pizzas",
                "icon": "",
                "description": "Delicious pizzas",
                "display_order": 1,
                "is_active": True
            },
            {
                "id": "cat_2",
                "name": "Burgers",
                "icon": "",
                "description": "Tasty burgers",
                "display_order": 2,
                "is_active": True
            }
        ])
        
        response = client.get("/api/test-restaurant/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Pizzas"
        assert data[1]["name"] == "Burgers"
    
    def test_get_products(self, client, mock_product_service):
        """Test get products endpoint"""
        mock_product_service.get_products_by_restaurant = AsyncMock(return_value=[
            {
                "id": "prod_1",
                "name": "Margherita Pizza",
                "description": "Classic pizza",
                "price": 15.99,
                "image": "",
                "category_id": "cat_1",
                "sizes": [],
                "toppings": [],
                "is_available": True,
                "is_popular": True,
                "is_vegetarian": True,
                "is_vegan": False,
                "allergens": [],
                "preparation_time": 20,
                "rating": 4.5,
                "rating_count": 100
            }
        ])
        
        response = client.get("/api/test-restaurant/products")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Margherita Pizza"
        assert data[0]["price"] == 15.99
    
    def test_create_order_success(self, client, mock_order_service):
        """Test successful order creation"""
        mock_order_service.create_order = AsyncMock(return_value={
            "id": "order_123",
            "order_number": "ORD-20240101-ABC123",
            "customer": {
                "name": "John Doe",
                "phone": "+1234567890",
                "email": "john @example.com",
                "address": "123 Main St",
                "delivery_notes": "Ring doorbell"
            },
            "items": [
                {
                    "product_id": "prod_1",
                    "product_name": "Margherita Pizza",
                    "quantity": 1,
                    "unit_price": 15.99,
                    "total_price": 15.99,
                    "customization": {}
                }
            ],
            "subtotal": 15.99,
            "delivery_fee": 2.50,
            "total": 18.49,
            "status": "pending",
            "payment_method": "whatsapp",
            "is_delivery": True,
            "estimated_delivery_time": "2024-01-01T01:00:00Z",
            "actual_delivery_time": None,
            "notes": None,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        })
        
        order_data = {
            "customer": {
                "name": "John Doe",
                "phone": "+1234567890",
                "email": "john @example.com",
                "address": "123 Main St",
                "delivery_notes": "Ring doorbell"
            },
            "items": [
                {
                    "product_id": "prod_1",
                    "product_name": "Margherita Pizza",
                    "quantity": 1,
                    "unit_price": 15.99,
                    "total_price": 15.99
                }
            ],
            "payment_method": "whatsapp",
            "is_delivery": True
        }
        
        response = client.post("/api/test-restaurant/orders", json=order_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["order_number"] == "ORD-20240101-ABC123"
        assert data["total"] == 18.49
    
    def test_create_order_validation_error(self, client):
        """Test order creation with invalid data"""
        invalid_order_data = {
            "customer": {
                "name": "",  # Empty name
                "phone": "invalid_phone"
            },
            "items": []  # Empty items array
        }
        
        response = client.post("/api/test-restaurant/orders", json=invalid_order_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "errors" in data
    
    def test_protected_endpoint_without_auth(self, client):
        """Test protected endpoint without authentication"""
        response = client.get("/api/test-restaurant/orders")
        
        assert response.status_code == 403  # Forbidden due to missing auth
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/test-restaurant/orders", headers=headers)
        
        assert response.status_code == 401  # Unauthorized
    
    def test_rate_limiting(self, client):
        """Test rate limiting middleware"""
        # This test would require mocking the rate limiter
        # or making multiple requests rapidly
        with patch('middleware.security.RateLimitMiddleware._is_rate_limited') as mock_rate_limit:
            mock_rate_limit.return_value = True
            
            response = client.get("/health")
            
            assert response.status_code == 429  # Too Many Requests
            data = response.json()
            assert "Rate limit exceeded" in data["error"]
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/api/restaurants/test-restaurant")
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get("/health")
        
        # Check for security headers
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"
        assert "x-correlation-id" in response.headers

# Fixture for running async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()