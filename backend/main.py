from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional, List
import os
import logging
from dotenv import load_dotenv

# Import modules
from db.mongo import database, init_db, close_db
from models import (
    TokenResponse, LoginRequest, RefreshTokenRequest, RestaurantResponse, RestaurantUpdate,
    CategoryResponse, CategoryCreate, CategoryUpdate, ProductResponse, ProductCreate, ProductUpdate,
    OrderResponse, OrderCreate, OrderStatusUpdate, RestaurantCreate
)
from services.auth import AuthService
from services.restaurants import RestaurantService
from services.products import ProductService
from services.orders import OrderService
from services.categories import CategoryService

# Import security middleware
from middleware.security import (
    RateLimitMiddleware, SecurityHeadersMiddleware, RequestLoggingMiddleware,
    InputValidationMiddleware, validation_exception_handler, http_exception_handler,
    general_exception_handler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Validate required environment variables
required_vars = ["MONGODB_URL", "SECRET_KEY", "DATABASE_NAME"]
for var in required_vars:
    if not os.getenv(var):
        raise RuntimeError(f"Missing required environment variable: {var}")

# Initialize services
auth_service = AuthService()
restaurant_service = RestaurantService()
product_service = ProductService()
order_service = OrderService()
category_service = CategoryService()

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting DUO Previa API...")
    await init_db()
    logger.info("Database connection established")
    yield
    # Shutdown
    logger.info("Shutting down DUO Previa API...")
    await close_db()
    logger.info("Database connection closed")

app = FastAPI(
    title="DUO Previa - Food Delivery API",
    description="API segura para plataforma de pedidos de comida multi-inquilino",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None,
)

# Add security middleware (order matters!)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(InputValidationMiddleware)

# Rate limiting (more restrictive for production)
rate_limit_calls = int(os.getenv("RATE_LIMIT_CALLS", "100"))
rate_limit_period = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))
app.add_middleware(RateLimitMiddleware, calls=rate_limit_calls, period=rate_limit_period)

# CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Dependency to get current user with enhanced validation
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Enhanced user authentication with logging"""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    try:
        token = credentials.credentials
        user = await auth_service.verify_token(token)
        
        if not user:
            logger.warning(
                "Invalid token used",
                extra={
                    "correlation_id": correlation_id,
                    "client_ip": request.headers.get("X-Forwarded-For", request.client.host)
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        logger.info(
            "User authenticated",
            extra={
                "correlation_id": correlation_id,
                "user_id": user["id"],
                "username": user["username"],
                "restaurant_slug": user["restaurant_slug"]
            }
        )
        
        return user
        
    except Exception as e:
        logger.error(
            "Authentication error",
            extra={
                "correlation_id": correlation_id,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

# Health check with enhanced information
@app.get("/health")
async def health_check():
    """Enhanced health check endpoint"""
    try:
        # Test database connection
        db = database.database
        await db.command("ping")
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable"
        )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "DUO Previa API v2.0.0",
        "status": "running",
        "documentation": "/docs" if os.getenv("ENVIRONMENT") == "development" else None
    }

# ===== AUTH ENDPOINTS =====
@app.post("/auth/login", response_model=TokenResponse)
async def login(request: Request, login_data: LoginRequest):
    """Login with enhanced security logging"""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.info(
        "Login attempt",
        extra={
            "correlation_id": correlation_id,
            "username": login_data.username,
            "restaurant_slug": login_data.restaurant_slug,
            "client_ip": request.headers.get("X-Forwarded-For", request.client.host)
        }
    )
    
    result = await auth_service.authenticate_user(
        login_data.username, 
        login_data.password, 
        login_data.restaurant_slug
    )
    
    if not result:
        logger.warning(
            "Login failed",
            extra={
                "correlation_id": correlation_id,
                "username": login_data.username,
                "restaurant_slug": login_data.restaurant_slug
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    logger.info(
        "Login successful",
        extra={
            "correlation_id": correlation_id,
            "user_id": result["user"]["id"],
            "username": result["user"]["username"]
        }
    )
    
    return result

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, refresh_data: RefreshTokenRequest):
    """Refresh token with logging"""
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    result = await auth_service.refresh_access_token(refresh_data.refresh_token)
    
    if not result:
        logger.warning(
            "Token refresh failed",
            extra={"correlation_id": correlation_id}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )
    
    logger.info(
        "Token refreshed",
        extra={
            "correlation_id": correlation_id,
            "user_id": result["user"]["id"]
        }
    )
    
    return result

# ===== RESTAURANT ENDPOINTS =====
@app.get("/api/restaurants/{slug}", response_model=RestaurantResponse)
async def get_restaurant_by_slug(slug: str):
    """Obtener información del restaurante por slug"""
    restaurant = await restaurant_service.get_by_slug(slug)
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurante no encontrado"
        )
    return restaurant

@app.put("/api/restaurants/{slug}")
async def update_restaurant(
    slug: str,
    restaurant_data: RestaurantUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Actualizar configuración del restaurante"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para este restaurante"
        )
    
    updated = await restaurant_service.update_restaurant(slug, restaurant_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurante no encontrado"
        )
    return {"message": "Restaurante actualizado exitosamente"}

# ===== CATEGORY ENDPOINTS =====
@app.get("/api/{slug}/categories", response_model=List[CategoryResponse])
async def get_categories(slug: str):
    """Obtener categorías del restaurante"""
    categories = await category_service.get_categories_by_restaurant(slug)
    return categories

@app.post("/api/{slug}/categories", response_model=CategoryResponse)
async def create_category(
    slug: str,
    category_data: CategoryCreate,
    current_user: dict = Depends(get_current_user)
):
    """Crear nueva categoría"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para este restaurante"
        )
    
    category = await category_service.create_category(slug, category_data)
    return category

@app.put("/api/{slug}/categories/{category_id}")
async def update_category(
    slug: str,
    category_id: str,
    category_data: CategoryUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Actualizar categoría"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    updated = await category_service.update_category(category_id, category_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"message": "Categoría actualizada"}

@app.delete("/api/{slug}/categories/{category_id}")
async def delete_category(
    slug: str,
    category_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Eliminar categoría"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    deleted = await category_service.delete_category(category_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"message": "Categoría eliminada"}

# ===== PRODUCT ENDPOINTS =====
@app.get("/api/{slug}/products", response_model=List[ProductResponse])
async def get_products(
    slug: str,
    category_id: Optional[str] = None,
    search: Optional[str] = None,
    popular_only: bool = False
):
    """Obtener productos del restaurante"""
    products = await product_service.get_products_by_restaurant(
        slug, category_id, search, popular_only
    )
    return products

@app.get("/api/{slug}/products/{product_id}", response_model=ProductResponse)
async def get_product(slug: str, product_id: str):
    """Obtener producto específico"""
    product = await product_service.get_product_by_id(product_id, slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return product

@app.post("/api/{slug}/products", response_model=ProductResponse)
async def create_product(
    slug: str,
    product_data: ProductCreate,
    current_user: dict = Depends(get_current_user)
):
    """Crear nuevo producto"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para este restaurante"
        )
    
    product = await product_service.create_product(slug, product_data)
    return product

@app.put("/api/{slug}/products/{product_id}")
async def update_product(
    slug: str,
    product_id: str,
    product_data: ProductUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Actualizar producto"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    updated = await product_service.update_product(product_id, product_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return {"message": "Producto actualizado exitosamente"}

@app.delete("/api/{slug}/products/{product_id}")
async def delete_product(
    slug: str,
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Eliminar producto"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    deleted = await product_service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"message": "Producto eliminado"}

# ===== ORDER ENDPOINTS =====
@app.post("/api/{slug}/orders", response_model=OrderResponse)
async def create_order(slug: str, order_data: OrderCreate):
    """Crear nuevo pedido"""
    order = await order_service.create_order(slug, order_data)
    return order

@app.get("/api/{slug}/orders", response_model=List[OrderResponse])
async def get_orders(
    slug: str,
    status_filter: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Obtener pedidos del restaurante"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    orders = await order_service.get_orders_by_restaurant(slug, status_filter, limit)
    return orders

@app.get("/api/{slug}/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    slug: str,
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener pedido específico"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    order = await order_service.get_order_by_id(order_id, slug)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return order

@app.put("/api/{slug}/orders/{order_id}/status")
async def update_order_status(
    slug: str,
    order_id: str,
    status_data: OrderStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Actualizar estado del pedido"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    updated = await order_service.update_order_status(order_id, status_data.status)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"message": "Estado del pedido actualizado"}

# ===== ANALYTICS ENDPOINTS =====
@app.get("/api/{slug}/analytics/dashboard")
async def get_dashboard_analytics(
    slug: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtener analíticas del dashboard"""
    if current_user["restaurant_slug"] != slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    analytics = await order_service.get_dashboard_analytics(slug)
    return analytics

# ===== SUPERADMIN ENDPOINTS =====
@app.post("/superadmin/restaurants", response_model=RestaurantResponse)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    current_user: dict = Depends(get_current_user)
):
    """Crear nuevo restaurante (solo superadmin)"""
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    restaurant = await restaurant_service.create_restaurant(restaurant_data)
    return restaurant

@app.get("/superadmin/restaurants", response_model=List[RestaurantResponse])
async def get_all_restaurants(current_user: dict = Depends(get_current_user)):
    """Obtener todos los restaurantes (solo superadmin)"""
    if current_user["role"] != "superadmin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    restaurants = await restaurant_service.get_all_restaurants()
    return restaurants

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
        log_level="info"
    )