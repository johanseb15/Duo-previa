from typing import List
from datetime import datetime
from db.mongo import get_collection
from utils.converters import to_object_id
from models import CategoryCreate, CategoryUpdate, CategoryResponse
import logging

logger = logging.getLogger(__name__)

class CategoryService:
    def __init__(self):
        self.collection = get_collection("categories")

    async def create_category(self, restaurant_slug: str, category_data: CategoryCreate) -> CategoryResponse:
        """Create new category"""
        try:
            from services.restaurants import RestaurantService
            restaurant_service = RestaurantService()
            restaurant = await restaurant_service.get_by_slug(restaurant_slug)
            if not restaurant:
                raise ValueError("Restaurant not found")
            
            category_doc = {
                "name": category_data.name,
                "icon": category_data.icon,
                "description": category_data.description,
                "restaurant_id": to_object_id(restaurant.id),
                "restaurant_slug": restaurant_slug,
                "display_order": category_data.display_order,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.collection.insert_one(category_doc)
            
            category_doc["id"] = str(result.inserted_id)
            return CategoryResponse(**category_doc)
            
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            raise

    async def get_categories_by_restaurant(self, restaurant_slug: str) -> List[CategoryResponse]:
        """Get categories by restaurant"""
        try:
            cursor = self.collection.find({
                "restaurant_slug": restaurant_slug,
                "is_active": True
            }).sort("display_order", 1)
            
            categories = []
            async for category in cursor:
                category["id"] = str(category["_id"])
                categories.append(CategoryResponse(**category))
                
            return categories
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []

    async def update_category(self, category_id: str, update_data: CategoryUpdate) -> bool:
        """Update category"""
        try:
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            if not update_dict:
                return True
                
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": to_object_id(category_id)},
                {"$set": update_dict}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating category: {e}")
            return False

    async def delete_category(self, category_id: str) -> bool:
        """Soft delete category"""
        try:
            result = await self.collection.update_one(
                {"_id": to_object_id(category_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return False