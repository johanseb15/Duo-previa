import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from services.auth import AuthService
from passlib.context import CryptContext

class TestAuthService:
    """Test suite for AuthService"""
    
    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance for testing"""
        with patch('services.auth.get_collection') as mock_collection:
            mock_collection.return_value = AsyncMock()
            return AuthService()
    
    def test_password_hashing(self, auth_service):
        """Test password hashing and verification"""
        password = "test_password_123"
        
        # Test hashing
        hashed = auth_service.get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
        
        # Test verification
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrong_password", hashed)
    
    def test_create_access_token(self, auth_service):
        """Test JWT access token creation"""
        data = {
            "sub": "testuser",
            "restaurant_slug": "test-restaurant",
            "role": "admin"
        }
        
        token = auth_service.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long
        assert token.count('.') == 2  # JWT has 3 parts separated by dots
    
    def test_create_refresh_token(self, auth_service):
        """Test JWT refresh token creation"""
        data = {
            "sub": "testuser",
            "restaurant_slug": "test-restaurant"
        }
        
        token = auth_service.create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 100
        assert token.count('.') == 2
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, auth_service):
        """Test successful user creation"""
        # Mock the collection
        auth_service.users_collection.find_one = AsyncMock(return_value=None)
        auth_service.users_collection.insert_one = AsyncMock(return_value=AsyncMock(inserted_id="user_id_123"))
        
        result = await auth_service.create_user(
            username="testuser",
            password="testpass123",
            restaurant_slug="test-restaurant"
        )
        
        assert result == "user_id_123"
        auth_service.users_collection.find_one.assert_called_once()
        auth_service.users_collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate(self, auth_service):
        """Test user creation with duplicate username"""
        # Mock existing user
        existing_user = {
            "_id": "existing_id",
            "username": "testuser",
            "restaurant_slug": "test-restaurant"
        }
        auth_service.users_collection.find_one = AsyncMock(return_value=existing_user)
        
        with pytest.raises(ValueError, match="User already exists"):
            await auth_service.create_user(
                username="testuser",
                password="testpass123",
                restaurant_slug="test-restaurant"
            )
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service):
        """Test successful user authentication"""
        # Mock user data
        mock_user = {
            "_id": "user_id_123",
            "username": "testuser",
            "password_hash": auth_service.get_password_hash("testpass123"),
            "role": "admin",
            "restaurant_slug": "test-restaurant",
            "is_active": True
        }
        
        auth_service.users_collection.find_one = AsyncMock(return_value=mock_user)
        
        result = await auth_service.authenticate_user(
            username="testuser",
            password="testpass123",
            restaurant_slug="test-restaurant"
        )
        
        assert result is not None
        assert result["access_token"]
        assert result["refresh_token"]
        assert result["user"]["username"] == "testuser"
        assert result["user"]["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, auth_service):
        """Test authentication with wrong password"""
        # Mock user data
        mock_user = {
            "_id": "user_id_123",
            "username": "testuser",
            "password_hash": auth_service.get_password_hash("correct_password"),
            "role": "admin",
            "restaurant_slug": "test-restaurant",
            "is_active": True
        }
        
        auth_service.users_collection.find_one = AsyncMock(return_value=mock_user)
        
        result = await auth_service.authenticate_user(
            username="testuser",
            password="wrong_password",
            restaurant_slug="test-restaurant"
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service):
        """Test authentication with non-existent user"""
        auth_service.users_collection.find_one = AsyncMock(return_value=None)
        
        result = await auth_service.authenticate_user(
            username="nonexistent",
            password="password123",
            restaurant_slug="test-restaurant"
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_verify_token_valid(self, auth_service):
        """Test token verification with valid token"""
        # Create a valid token
        data = {
            "sub": "testuser",
            "restaurant_slug": "test-restaurant",
            "role": "admin",
            "user_id": "user_id_123"
        }
        token = auth_service.create_access_token(data)
        
        # Mock user data
        mock_user = {
            "_id": "user_id_123",
            "username": "testuser",
            "role": "admin",
            "restaurant_slug": "test-restaurant",
            "is_active": True
        }
        
        auth_service.users_collection.find_one = AsyncMock(return_value=mock_user)
        
        result = await auth_service.verify_token(token)
        
        assert result is not None
        assert result["username"] == "testuser"
        assert result["role"] == "admin"
        assert result["restaurant_slug"] == "test-restaurant"
    
    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, auth_service):
        """Test token verification with invalid token"""
        result = await auth_service.verify_token("invalid_token")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, auth_service):
        """Test successful token refresh"""
        # Create a valid refresh token
        data = {
            "sub": "testuser",
            "restaurant_slug": "test-restaurant",
            "role": "admin",
            "user_id": "user_id_123"
        }
        refresh_token = auth_service.create_refresh_token(data)
        
        # Mock user data
        mock_user = {
            "_id": "user_id_123",
            "username": "testuser",
            "role": "admin",
            "restaurant_slug": "test-restaurant",
            "is_active": True
        }
        
        auth_service.users_collection.find_one = AsyncMock(return_value=mock_user)
        
        result = await auth_service.refresh_access_token(refresh_token)
        
        assert result is not None
        assert result["access_token"]
        assert result["refresh_token"]
        assert result["user"]["username"] == "testuser"
    
    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid(self, auth_service):
        """Test token refresh with invalid token"""
        result = await auth_service.refresh_access_token("invalid_refresh_token")
        assert result is None

# Fixture for running async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()