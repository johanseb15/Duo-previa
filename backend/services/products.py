from typing import List, Optional
from datetime import datetime
from db.mongo import get_collection
from utils.converters import to_object_id
from models import ProductCreate, ProductUpdate, ProductResponse, ProductSize, ProductTopping
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self):
        self.collection = get_collection("products")

    async def create_product(self, restaurant_slug: str, product_data: ProductCreate) -> ProductResponse:
        """Create new product"""
        try:
            from services.restaurants import RestaurantService
            restaurant_service = RestaurantService()
            restaurant = await restaurant_service.get_by_slug(restaurant_slug)
            if not restaurant:
                raise ValueError("Restaurant not found")
            
            product_doc = {
                "name": product_data.name,
                "description": product_data.description,
                "price": product_data.price,
                "image": product_data.image,
                "category_id": to_object_id(product_data.category_id),
                "restaurant_id": to_object_id(restaurant.id),
                "restaurant_slug": restaurant_slug,
                "sizes": [size.dict() for size in product_data.sizes],
                "toppings": [topping.dict() for topping in product_data.toppings],
                "is_available": True,
                "is_popular": product_data.is_popular,
                "is_vegetarian": product_data.is_vegetarian,
                "is_vegan": product_data.is_vegan,
                "allergens": product_data.allergens,
                "preparation_time": product_data.preparation_time,
                "rating": 5.0,
                "rating_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.collection.insert_one(product_doc)
            
            product_doc["id"] = str(result.inserted_id)
            product_doc["category_id"] = str(product_doc["category_id"])
            product_doc["sizes"] = [ProductSize(**size) for size in product_doc["sizes"]]
            product_doc["toppings"] = [ProductTopping(**topping) for topping in product_doc["toppings"]]
            
            return ProductResponse(**product_doc)
            
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise

    async def get_products_by_restaurant(
        self,
        restaurant_slug: str,
        category_id: Optional[str] = None,
        search: Optional[str] = None,
        popular_only: bool = False
    ) -> List[ProductResponse]:
        """Get products by restaurant with filters"""
        try:
            query = {
                "restaurant_slug": restaurant_slug,
                "is_available": True
            }
            
            if category_id:
                query["category_id"] = to_object_id(category_id)
                
            if search:
                query["name"] = {"$regex": search, "$options": "i"}
                
            if popular_only:
                query["is_popular"] = True
            
            cursor = self.collection.find(query).sort("name", 1)
            
            products = []
            async for product in cursor:
                product["id"] = str(product["_id"])
                product["category_id"] = str(product["category_id"])
                product["sizes"] = [ProductSize(**size) for size in product.get("sizes", [])]
                product["toppings"] = [ProductTopping(**topping) for topping in product.get("toppings", [])]
                products.append(ProductResponse(**product))
                
            return products
            
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []

    async def get_product_by_id(self, product_id: str, restaurant_slug: str) -> Optional[ProductResponse]:
        """Get product by ID"""
        try:
            product = await self.collection.find_one({
                "_id": to_object_id(product_id),
                "restaurant_slug": restaurant_slug,
                "is_available": True
            })
            
            if not product:
                return None
                
            product["id"] = str(product["_id"])
            product["category_id"] = str(product["category_id"])
            product["sizes"] = [ProductSize(**size) for size in product.get("sizes", [])]
            product["toppings"] = [ProductTopping(**topping) for topping in product.get("toppings", [])]
            
            return ProductResponse(**product)
            
        except Exception as e:
            logger.error(f"Error getting product: {e}")
            return None

    async def update_product(self, product_id: str, update_data: ProductUpdate) -> bool:
        """Update product"""
        try:
            update_dict = {}
            
            for field, value in update_data.dict().items():
                if value is not None:
                    if field == "category_id":
                        update_dict[field] = to_object_id(value)
                    elif field in ["sizes", "toppings"]:
                        update_dict[field] = [item.dict() for item in value] if value else []
                    else:
                        update_dict[field] = value
            
            if not update_dict:
                return True
                
            update_dict["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": to_object_id(product_id)},
                {"$set": update_dict}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            return False

    async def delete_product(self, product_id: str) -> bool:
        """Soft delete product"""
        try:
            result = await self.collection.update_one(
                {"_id": to_object_id(product_id)},
                {"$set": {"is_available": False, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False