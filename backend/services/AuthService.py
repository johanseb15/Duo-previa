from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from models import User, TokenResponse, LoginRequest, RefreshTokenRequest
from database import database

class AuthService:
    def __init__(self):
        self.SECRET_KEY = "your-super-secret-jwt-key" # TODO: Get from env
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.REFRESH_TOKEN_EXPIRE_DAYS = 7
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def authenticate_user(self, username: str, password: str, restaurant_slug: str):
        user_data = await database.users.find_one({"username": username, "restaurant_id": restaurant_slug})
        if not user_data:
            return False
        user = User(**user_data)
        if not self.verify_password(password, user.hashed_password):
            return False
        
        access_token = self.create_access_token({"sub": user.username, "restaurant_slug": user.restaurant_id, "role": user.role})
        refresh_token = self.create_refresh_token({"sub": user.username, "restaurant_slug": user.restaurant_id, "role": user.role})
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    async def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            restaurant_slug: str = payload.get("restaurant_slug")
            role: str = payload.get("role")
            if username is None or restaurant_slug is None or role is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
            return {"username": username, "restaurant_slug": restaurant_slug, "role": role}
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    async def refresh_access_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            restaurant_slug: str = payload.get("restaurant_slug")
            role: str = payload.get("role")
            if username is None or restaurant_slug is None or role is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload")
            
            # Check if refresh token is valid (e.g., not revoked, not expired if not handled by JWT exp)
            # For simplicity, we just create a new access token
            new_access_token = self.create_access_token({"sub": username, "restaurant_slug": restaurant_slug, "role": role})
            return TokenResponse(access_token=new_access_token, refresh_token=refresh_token, token_type="bearer")
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate refresh token")
