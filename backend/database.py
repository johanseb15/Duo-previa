import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

database = Database()

async def get_database():
    return database.database

async def init_db():
    """Initialize database connection"""
    try:
        # MongoDB connection string
        mongodb_url = os.getenv(
            "MONGODB_URL", 
            "mongodb://localhost:27017"
        )
        
        database_name = os.getenv("DATABASE_NAME", "food_delivery_multi")
        
        # Create client
        database.client = AsyncIOMotorClient(
            mongodb_url,
            maxPoolSize=10,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )
        
        # Get database
        database.database = database.client[database_name]
        
        # Test connection
        await database.client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB: {database_name}")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

async def create_indexes():
    """Create database indexes for better performance"""
    db = database.database
    
    try:
        # Restaurant indexes
        await db.restaurants.create_index("slug", unique=True)
        await db.restaurants.create_index("email", unique=True)
        await db.restaurants.create_index([("is_active", 1), ("created_at", -1)])
        
        # User indexes
        await db.users.create_index("username")
        await db.users.create_index("restaurant_slug")
        await db.users.create_index([("username", 1), ("restaurant_slug", 1)], unique=True)
        
        # Product indexes
        await db.products.create_index("restaurant_slug")
        await db.products.create_index("category_id")
        await db.products.create_index([("restaurant_slug", 1), ("is_available", 1)])
        await db.products.create_index([("restaurant_slug", 1), ("is_popular", 1)])
        await db.products.create_index("name", background=True)  # Text search
        
        # Order indexes
        await db.orders.create_index("restaurant_slug")
        await db.orders.create_index("order_number", unique=True)
        await db.orders.create_index([("restaurant_slug", 1), ("status", 1)])
        await db.orders.create_index([("restaurant_slug", 1), ("created_at", -1)])
        await db.orders.create_index("customer.phone")
        
        # Category indexes
        await db.categories.create_index("restaurant_slug")
        await db.categories.create_index([("restaurant_slug", 1), ("display_order", 1)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

async def close_db():
    """Close database connection"""
    if database.client:
        database.client.close()
        logger.info("Database connection closed")

# Collections helper
def get_collection(collection_name: str):
    """Get collection by name"""
    return database.database[collection_name]

# Multi-tenant helpers
def get_restaurant_filter(restaurant_slug: str) -> dict:
    """Get filter for restaurant-specific queries"""
    return {"restaurant_slug": restaurant_slug}

def get_active_restaurant_filter(restaurant_slug: str) -> dict:
    """Get filter for active restaurant queries"""
    return {
        "restaurant_slug": restaurant_slug,
        "is_active": True
    }

# Aggregation helpers
def get_restaurant_pipeline(restaurant_slug: str) -> list:
    """Get aggregation pipeline for restaurant queries"""
    return [
        {"$match": {"restaurant_slug": restaurant_slug}},
        {"$sort": {"created_at": -1}}
    ]

def get_products_with_category_pipeline(restaurant_slug: str) -> list:
    """Get products with category information"""
    return [
        {"$match": {"restaurant_slug": restaurant_slug, "is_available": True}},
        {
            "$lookup": {
                "from": "categories",
                "localField": "category_id",
                "foreignField": "_id",
                "as": "category"
            }
        },
        {"$unwind": "$category"},
        {"$sort": {"category.display_order": 1, "name": 1}}
    ]

def get_orders_analytics_pipeline(restaurant_slug: str, start_date, end_date) -> list:
    """Get orders analytics pipeline"""
    return [
        {
            "$match": {
                "restaurant_slug": restaurant_slug,
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                },
                "status": {"$ne": "cancelled"}
            }
        },
        {
            "$group": {
                "_id": {
                    "hour": {"$hour": "$created_at"},
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}
                },
                "count": {"$sum": 1},
                "revenue": {"$sum": "$total"}
            }
        },
        {"$sort": {"_id.date": 1, "_id.hour": 1}}
    ]

# Migration helpers
async def migrate_data():
    """Run data migrations if needed"""
    db = database.database
    
    # Example: Add restaurant_slug to existing documents
    # This would run only once during deployment
    
    try:
        # Check if