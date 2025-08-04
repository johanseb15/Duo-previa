from typing import Optional, List
from models import Restaurant, RestaurantCreate, RestaurantUpdate, RestaurantResponse, RestaurantSettings, CategoryCreate
from db.mongo import database
from utils import with_transaction
from utils import to_object_id, to_string_id
from utils import to_object_id, to_string_id
from services.auth import AuthService
from services.categories import CategoryService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RestaurantService:
    def __init__(self):
        self.collection = database.restaurants
        self.auth_service = AuthService()

    async def create_restaurant(self, restaurant_data: RestaurantCreate) -> RestaurantResponse:
        """Create new restaurant with admin user"""
        try:
            async def operation(session):
                # Check if slug is unique
                existing = await self.collection.find_one({"slug": restaurant_data.slug})
                if existing:
                    raise ValueError("Restaurant slug already exists")
                
                # Create restaurant
                restaurant_doc = {
                    "name": restaurant_data.name,
                    "slug": restaurant_data.slug,
                    "description": restaurant_data.description,
                    "logo": restaurant_data.logo,
                    "email": restaurant_data.email,
                    "phone": restaurant_data.phone,
                    "address": restaurant_data.address,
                    "city": restaurant_data.city,
                    "country": restaurant_data.country,
                    "settings": RestaurantSettings().dict(),
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = await self.collection.insert_one(restaurant_doc, session=session)
                restaurant_id = result.inserted_id
                
                # Create admin user
                await self.auth_service.create_user(
                    username=restaurant_data.admin_username,
                    password=restaurant_data.admin_password,
                    restaurant_slug=restaurant_data.slug,
                    role="admin"
                )
                
                # Create default categories
                categories_service = CategoryService()
                default_categories = [
                    {"name": "Pizzas", "icon": "🍕", "display_order": 1},
                    {"name": "Hamburguesas", "icon": "🍔", "display_order": 2},
                    {"name": "Empanadas", "icon": "🥟", "display_order": 3},
                    {"name": "Bebidas", "icon": "🥤", "display_order": 4},
                    {"name": "Postres", "icon": "🍰", "display_order": 5},
                ]
                
                for cat_data in default_categories:
                    await categories_service.create_category(
                        restaurant_data.slug,
                        CategoryCreate(**cat_data)
                    )
                
                # Return created restaurant
                restaurant_doc["id"] = str(restaurant_id)
                restaurant_doc["settings"] = RestaurantSettings(**restaurant_doc["settings"])
                
                return RestaurantResponse(**restaurant_doc)
            
            return await with_transaction(operation)
            
        except Exception as e:
            logger.error(f"Error creating restaurant: {e}")
            raise

    async def get_by_slug(self, slug: str) -> Optional[RestaurantResponse]:
        """Get restaurant by slug"""
        try:
            restaurant = await self.collection.find_one({"slug": slug, "is_active": True})
            if not restaurant:
                return None
                
            restaurant["id"] = str(restaurant["_id"])
            restaurant["settings"] = RestaurantSettings(**restaurant["settings"])
            
            return RestaurantResponse(**restaurant)
            
        except Exception as e:
            logger.error(f"Error getting restaurant by slug: {e}")
            return None

    async def update_restaurant(self, slug: str, update_data: RestaurantUpdate) -> bool:
        """Update restaurant"""
        try:
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            if not update_dict:
                return True
                
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"slug": slug},
                {"$set": update_dict}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating restaurant: {e}")
            return False

    async def get_all_restaurants(self) -> List[RestaurantResponse]:
        """Get all restaurants (superadmin only)"""
        try:
            cursor = self.collection.find({}).sort("created_at", -1)
            restaurants = []
            
            async for restaurant in cursor:
                restaurant["id"] = str(restaurant["_id"])
                restaurant["settings"] = RestaurantSettings(**restaurant["settings"])
                restaurants.append(RestaurantResponse(**restaurant))
                
            return restaurants
            
        except Exception as e:
            logger.error(f"Error getting all restaurants: {e}")
            return []
