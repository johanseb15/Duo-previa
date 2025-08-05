from typing import List, Optional
from datetime import datetime, timedelta
from db.mongo import get_collection
from utils.converters import to_object_id
from models import OrderCreate, OrderResponse, OrderStatus, CustomerInfo, OrderItem, DashboardAnalytics
import uuid
import logging

logger = logging.getLogger(__name__)

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
            from services.restaurants import RestaurantService
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
            query = {
                "restaurant_slug": restaurant_slug,
                "is_active": True
            }
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
                "restaurant_slug": restaurant_slug,
                "is_active": True
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
            ]