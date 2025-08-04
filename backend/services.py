from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from database import get_collection, to_object_id, to_string_id, with_transaction
from models import *
from auth import AuthService
import logging
import uuid

logger = logging.getLogger(__name__)

class RestaurantService:
    def __init__(self):
        self.collection = get_collection("restaurants")
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
                    {"name": " Pizzas", "icon": "", "display_order": 1},
                    {"name": " Ensaladas", "icon": "", "display_order": 2},
                    {"name": " Bebidas", "icon": "", "display_order": 3},
                    {"name": " Postres", "icon": "", "display_order": 4},
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

class CategoryService:
    def __init__(self):
        self.collection = get_collection("categories")

    async def create_category(self, restaurant_slug: str, category_data: CategoryCreate) -> CategoryResponse:
        """Create new category"""
        try:
            # Get restaurant
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

class ProductService:
    def __init__(self):
        self.collection = get_collection("products")

    async def create_product(self, restaurant_slug: str, product_data: ProductCreate) -> ProductResponse:
        """Create new product"""
        try:
            # Get restaurant
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

class OrderService:
    def __init__(self):
        self.collection = get_collection("orders")

    def generate_order_number(self) -> str:
        """Generate unique order number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"

    async def create_order(self, restaurant_slug: str, order_data: OrderCreate) -> OrderResponse:
        """Create new order"""
        try:
            # Get restaurant
            restaurant_service = RestaurantService()
            restaurant = await restaurant_service.get_by_slug(restaurant_slug)
            if not restaurant:
                raise ValueError("Restaurant not found")
            
            # Calculate totals
            subtotal = sum(item.total_price for item in order_data.items)
            delivery_fee = restaurant.settings.delivery_fee if order_data.is_delivery else 0.0
            total = subtotal + delivery_fee
            
            # Estimate delivery time
            estimated_delivery = None
            if order_data.is_delivery:
                estimated_delivery = datetime.utcnow() + timedelta(minutes=45)
            
            order_doc = {
                "order_number": self.generate_order_number(),
                "restaurant_id": to_object_id(restaurant.id),
                "restaurant_slug": restaurant_slug,
                "customer": order_data.customer.dict(),
                "items": [item.dict() for item in order_data.items],
                "subtotal": subtotal,
                "delivery_fee": delivery_fee,
                "total": total,
                "status": OrderStatus.PENDING,
                "payment_method": order_data.payment_method,
                "is_delivery": order_data.is_delivery,
                "estimated_delivery_time": estimated_delivery,
                "notes": order_data.notes,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.collection.insert_one(order_doc)
            
            order_doc["id"] = str(result.inserted_id)
            order_doc["customer"] = CustomerInfo(**order_doc["customer"])
            order_doc["items"] = [OrderItem(**item) for item in order_doc["items"]]
            
            return OrderResponse(**order_doc)
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise

    async def get_orders_by_restaurant(
        self,
        restaurant_slug: str,
        status_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[OrderResponse]:
        """Get orders by restaurant"""
        try:
            query = {"restaurant_slug": restaurant_slug}
            if status_filter:
                query["status"] = status_filter
            
            cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
            
            orders = []
            async for order in cursor:
                order["id"] = str(order["_id"])
                order["customer"] = CustomerInfo(**order["customer"])
                order["items"] = [OrderItem(**item) for item in order["items"]]
                orders.append(OrderResponse(**order))
                
            return orders
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return []

    async def get_order_by_id(self, order_id: str, restaurant_slug: str) -> Optional[OrderResponse]:
        """Get specific order"""
        try:
            order = await self.collection.find_one({
                "_id": to_object_id(order_id),
                "restaurant_slug": restaurant_slug
            })
            
            if not order:
                return None
                
            order["id"] = str(order["_id"])
            order["customer"] = CustomerInfo(**order["customer"])
            order["items"] = [OrderItem(**item) for item in order["items"]]
            
            return OrderResponse(**order)
            
        except Exception as e:
            logger.error(f"Error getting order: {e}")
            return None

    async def update_order_status(self, order_id: str, new_status: str) -> bool:
        """Update order status"""
        try:
            result = await self.collection.update_one(
                {"_id": to_object_id(order_id)},
                {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False

    async def get_dashboard_analytics(self, restaurant_slug: str) -> DashboardAnalytics:
        """Get dashboard analytics for a restaurant"""
        try:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            total_orders_today = await self.collection.count_documents({
                "restaurant_slug": restaurant_slug,
                "created_at": {"$gte": today}
            })
            
            total_revenue_today_pipeline = [
                {"$match": {
                    "restaurant_slug": restaurant_slug,
                    "created_at": {"$gte": today},
                    "status": {"$ne": OrderStatus.CANCELLED}
                }},
                {"$group": {"_id": None, "total_revenue": {"$sum": "$total"}}}
            ]
            
            total_revenue_today_result = await self.collection.aggregate(total_revenue_today_pipeline).to_list(length=1)
            total_revenue_today = total_revenue_today_result[0]["total_revenue"] if total_revenue_today_result else 0.0
            
            pending_orders = await self.collection.count_documents({
                "restaurant_slug": restaurant_slug,
                "status": OrderStatus.PENDING
            })
            
            # Popular products (example: top 5 products by quantity sold today)
            popular_products_pipeline = [
                {"$match": {
                    "restaurant_slug": restaurant_slug,
                    "created_at": {"$gte": today},
                    "status": {"$ne": OrderStatus.CANCELLED}
                }},
                {"$unwind": "$items"},
                {"$group": {
                    "_id": "$items.product_name",
                    "total_quantity": {"$sum": "$items.quantity"}
                }},
                {"$sort": {"total_quantity": -1}},
                {"$limit": 5}
            ]
            popular_products = await self.collection.aggregate(popular_products_pipeline).to_list(length=None)
            
            # Recent orders
            recent_orders_cursor = self.collection.find({"restaurant_slug": restaurant_slug}).sort("created_at", -1).limit(5)
            recent_orders = []
            async for order in recent_orders_cursor:
                order["id"] = str(order["_id"])
                order["customer"] = CustomerInfo(**order["customer"])
                order["items"] = [OrderItem(**item) for item in order["items"]]
                recent_orders.append(OrderResponse(**order))
            
            # Hourly orders (example for last 24 hours)
            hourly_orders_pipeline = [
                {"$match": {
                    "restaurant_slug": restaurant_slug,
                    "created_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
                }},
                {"$group": {
                    "_id": {"$hour": "$created_at"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            hourly_orders = await self.collection.aggregate(hourly_orders_pipeline).to_list(length=None)
            
            return DashboardAnalytics(
                total_orders_today=total_orders_today,
                total_revenue_today=total_revenue_today,
                pending_orders=pending_orders,
                popular_products=popular_products,
                recent_orders=recent_orders,
                hourly_orders=hourly_orders
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard analytics: {e}")
            raise
