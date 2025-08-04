import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from passlib.context import CryptContext
from jose import JWTError, jwt
from db.mongo import get_collection
from utils.converters import to_object_id, to_string_id
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.users_collection = get_collection("users")
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("SECRET_KEY", "super-secret-key")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: dict):
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)  # Refresh token lasts 7 days
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def create_user(self, username: str, password: str, restaurant_slug: str, role: str = "admin"):
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await self.users_collection.find_one({
                "username": username,
                "restaurant_slug": restaurant_slug
            })
            
            if existing_user:
                raise ValueError("User already exists")

            user_doc = {
                "username": username,
                "password_hash": self.get_password_hash(password),
                "role": role,
                "restaurant_slug": restaurant_slug,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            result = await self.users_collection.insert_one(user_doc)
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    async def authenticate_user(self, username: str, password: str, restaurant_slug: str) -> Optional[Dict]:
        """Authenticate user and return tokens"""
        try:
            user = await self.users_collection.find_one({
                "username": username,
                "restaurant_slug": restaurant_slug,
                "is_active": True
            })

            if not user or not self.verify_password(password, user["password_hash"]):
                return None

            # Create tokens
            token_data = {
                "sub": user["username"],
                "restaurant_slug": restaurant_slug,
                "role": user["role"],
                "user_id": str(user["_id"])
            }

            access_token = self.create_access_token(data=token_data)
            refresh_token = self.create_refresh_token(data=token_data)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "user": {
                    "id": str(user["_id"]),
                    "username": user["username"],
                    "role": user["role"],
                    "restaurant_slug": restaurant_slug
                }
            }

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            username = payload.get("sub")
            restaurant_slug = payload.get("restaurant_slug")
            token_type = payload.get("type")

            if not username or not restaurant_slug or token_type != "refresh":
                return None

            # Get user to verify it still exists and is active
            user = await self.users_collection.find_one({
                "username": username,
                "restaurant_slug": restaurant_slug,
                "is_active": True
            })

            if not user:
                return None

            # Create new tokens
            token_data = {
                "sub": user["username"],
                "restaurant_slug": restaurant_slug,
                "role": user["role"],
                "user_id": str(user["_id"])
            }

            access_token = self.create_access_token(data=token_data)
            new_refresh_token = self.create_refresh_token(data=token_data)

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "user": {
                    "id": str(user["_id"]),
                    "username": user["username"],
                    "role": user["role"],
                    "restaurant_slug": restaurant_slug
                }
            }

        except JWTError as e:
            logger.error(f"JWT Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None

    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return user data"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username = payload.get("sub")
            restaurant_slug = payload.get("restaurant_slug")

            if not username or not restaurant_slug:
                return None

            # Get user to verify it still exists and is active
            user = await self.users_collection.find_one({
                "username": username,
                "restaurant_slug": restaurant_slug,
                "is_active": True
            })

            if not user:
                return None

            return {
                "id": str(user["_id"]),
                "username": user["username"],
                "role": user["role"],
                "restaurant_slug": restaurant_slug
            }

        except JWTError as e:
            logger.error(f"JWT Error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None