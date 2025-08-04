from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
import datetime # Importar el módulo datetime completo
from enum import Enum
from bson import ObjectId
from pydantic_core import core_schema

# Utility class for ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # This is the correct method for Pydantic v2
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema

# Enums
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class UserRole(str, Enum):
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    CUSTOMER = "customer"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    WHATSAPP = "whatsapp"
    TRANSFER = "transfer"

# ===== BASE MODELS =====
class BaseDocument(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow) # Usar datetime.datetime
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow) # Usar datetime.datetime

    class Config:
        validate_by_name = True # Renombrado de allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# ===== RESTAURANT MODELS =====
class RestaurantColors(BaseModel):
    primary: str = "#FF6B35"
    secondary: str = "#F7931E"
    accent: str = "#FFD23F"

class DeliveryZone(BaseModel):
    name: str
    delivery_fee: float = 0.0
    min_order: float = 0.0
    delivery_time: str = "30-45 min"

class RestaurantSettings(BaseModel):
    colors: RestaurantColors = RestaurantColors()
    delivery_zones: List[DeliveryZone] = []
    min_order_amount: float = 0.0
    delivery_fee: float = 0.0
    is_open: bool = True
    opening_hours: Dict[str, Dict[str, str]] = {}
    accept_cash: bool = True
    accept_cards: bool = False

class Restaurant(BaseDocument):
    name: str
    slug: str = Field(..., pattern="^[a-z0-9-]+$") # Changed regex to pattern
    description: Optional[str] = None
    logo: str = ""
    email: EmailStr
    phone: str
    address: str
    city: str = "Córdoba"
    country: str = "Argentina"
    settings: RestaurantSettings = RestaurantSettings()
    is_active: bool = True

class RestaurantCreate(BaseModel):
    name: str
    slug: str = Field(..., pattern="^[a-z0-9-]+$") # Changed regex to pattern
    description: Optional[str] = None
    logo: str = ""
    email: EmailStr
    phone: str
    address: str
    city: str = "Córdoba"
    country: str = "Argentina"
    admin_username: str
    admin_password: str

class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    settings: Optional[RestaurantSettings] = None

class RestaurantResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str]
    logo: str
    phone: str
    address: str
    city: str
    settings: RestaurantSettings
    is_active: bool
    created_at: datetime.datetime # Usar datetime.datetime

# ===== USER MODELS =====
class User(BaseDocument):
    username: str
    email: Optional[EmailStr] = None
    password_hash: str
    role: UserRole = UserRole.ADMIN
    restaurant_id: Optional[PyObjectId] = None
    restaurant_slug: Optional[str] = None
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str
    role: UserRole = UserRole.ADMIN
    restaurant_slug: str

# ===== CATEGORY MODELS =====
class Category(BaseDocument):
    name: str
    icon: str = "️"
    description: Optional[str] = None
    restaurant_id: PyObjectId
    restaurant_slug: str
    display_order: int = 0
    is_active: bool = True

class CategoryCreate(BaseModel):
    name: str
    icon: str = "️"
    description: Optional[str] = None
    display_order: int = 0

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class CategoryResponse(BaseModel):
    id: str
    name: str
    icon: str
    description: Optional[str]
    display_order: int
    is_active: bool

# ===== PRODUCT MODELS =====
class ProductSize(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class ProductTopping(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    is_vegetarian: bool = False

class Product(BaseDocument):
    name: str
    description: str
    price: float  # Precio base
    image: str = "️"
    category_id: PyObjectId
    restaurant_id: PyObjectId
    restaurant_slug: str
    sizes: List[ProductSize] = []
    toppings: List[ProductTopping] = []
    is_available: bool = True
    is_popular: bool = False
    is_vegetarian: bool = False
    is_vegan: bool = False
    allergens: List[str] = []
    preparation_time: int = 15  # minutos
    rating: float = 5.0
    rating_count: int = 0

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image: str = "️"
    category_id: str
    sizes: List[ProductSize] = []
    toppings: List[ProductTopping] = []
    is_popular: bool = False
    is_vegetarian: bool = False
    is_vegan: bool = False
    allergens: List[str] = []
    preparation_time: int = 15

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    category_id: Optional[str] = None
    sizes: Optional[List[ProductSize]] = None
    toppings: Optional[List[ProductTopping]] = None
    is_available: Optional[bool] = None
    is_popular: Optional[bool] = None
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    allergens: Optional[List[str]] = None
    preparation_time: Optional[int] = None

class ProductResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    image: str
    category_id: str
    sizes: List[ProductSize]
    toppings: List[ProductTopping]
    is_available: bool
    is_popular: bool
    is_vegetarian: bool
    is_vegan: bool
    allergens: List[str]
    preparation_time: int
    rating: float
    rating_count: int

# ===== ORDER MODELS =====
class OrderItemCustomization(BaseModel):
    size: Optional[str] = None
    toppings: List[str] = []
    special_instructions: Optional[str] = None

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    customization: OrderItemCustomization = OrderItemCustomization()

class CustomerInfo(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    delivery_notes: Optional[str] = None

class Order(BaseDocument):
    order_number: str
    restaurant_id: PyObjectId
    restaurant_slug: str
    customer: CustomerInfo
    items: List[OrderItem]
    subtotal: float
    delivery_fee: float = 0.0
    total: float
    status: OrderStatus = OrderStatus.PENDING
    payment_method: PaymentMethod = PaymentMethod.WHATSAPP
    is_delivery: bool = True
    estimated_delivery_time: Optional[datetime.datetime] = None # Usar datetime.datetime
    actual_delivery_time: Optional[datetime.datetime] = None # Usar datetime.datetime
    notes: Optional[str] = None

class OrderCreate(BaseModel):
    customer: CustomerInfo
    items: List[OrderItem]
    payment_method: PaymentMethod = PaymentMethod.WHATSAPP
    is_delivery: bool = True
    notes: Optional[str] = None

    from pydantic import field_validator

    @field_validator('items')
    @classmethod
    def items_not_empty(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderResponse(BaseModel):
    id: str
    order_number: str
    customer: CustomerInfo
    items: List[OrderItem]
    subtotal: float
    delivery_fee: float
    total: float
    status: OrderStatus
    payment_method: PaymentMethod
    is_delivery: bool
    estimated_delivery_time: Optional[datetime.datetime] # Usar datetime.datetime
    actual_delivery_time: Optional[datetime.datetime] # Usar datetime.datetime
    notes: Optional[str]
    created_at: datetime.datetime # Usar datetime.datetime
    updated_at: datetime.datetime # Usar datetime.datetime

# ===== AUTH MODELS =====
class LoginRequest(BaseModel):
    username: str
    password: str
    restaurant_slug: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

# ===== ANALYTICS MODELS =====
class DashboardAnalytics(BaseModel):
    total_orders_today: int
    total_revenue_today: float
    pending_orders: int
    popular_products: List[Dict[str, Any]]
    recent_orders: List[OrderResponse]
    hourly_orders: List[Dict[str, Any]]

# ===== WEBHOOK MODELS =====
class WebhookEvent(BaseModel):
    event_type: str
    restaurant_slug: str
    data: Dict[str, Any]
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow) # Usar datetime.datetime

__all__ = [
    "PyObjectId", "OrderStatus", "UserRole", "PaymentMethod", "BaseDocument",
    "RestaurantColors", "DeliveryZone", "RestaurantSettings", "Restaurant", "RestaurantCreate", "RestaurantUpdate", "RestaurantResponse",
    "User", "UserCreate",
    "Category", "CategoryCreate", "CategoryUpdate", "CategoryResponse",
    "ProductSize", "ProductTopping", "Product", "ProductCreate", "ProductUpdate", "ProductResponse",
    "OrderItemCustomization", "OrderItem", "CustomerInfo", "Order", "OrderCreate", "OrderStatusUpdate", "OrderResponse",
    "LoginRequest", "RefreshTokenRequest", "TokenResponse",
    "DashboardAnalytics", "WebhookEvent"
]