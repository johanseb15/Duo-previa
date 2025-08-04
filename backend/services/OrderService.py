from typing import Optional, List
from models import Order, OrderCreate, OrderStatusUpdate
from database import database
from bson import ObjectId

class OrderService:
    async def create_order(self, slug: str, order_data: OrderCreate) -> Order:
        order = Order(restaurant_id=slug, **order_data.dict())
        await database.orders.insert_one(order.dict(by_alias=True))
        return order

    async def get_orders_by_restaurant(self, slug: str, status_filter: Optional[str], limit: int) -> List[Order]:
        query = {"restaurant_id": slug}
        if status_filter:
            query["status"] = status_filter
        
        orders = []
        async for o in database.orders.find(query).limit(limit):
            orders.append(Order(**o))
        return orders

    async def get_order_by_id(self, order_id: str, restaurant_slug: str) -> Optional[Order]:
        order_data = await database.orders.find_one({"_id": ObjectId(order_id), "restaurant_id": restaurant_slug})
        if order_data:
            return Order(**order_data)
        return None

    async def update_order_status(self, order_id: str, new_status: str) -> bool:
        update_result = await database.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": new_status}}
        )
        return update_result.modified_count > 0

    async def get_dashboard_analytics(self, slug: str) -> dict:
        # Implementar lógica de analíticas aquí (ej. conteo de pedidos por estado, ventas totales)
        total_orders = await database.orders.count_documents({"restaurant_id": slug})
        pending_orders = await database.orders.count_documents({"restaurant_id": slug, "status": "pending"})
        completed_orders = await database.orders.count_documents({"restaurant_id": slug, "status": "completed"})
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "sales_today": 0 # Placeholder
        }
