from typing import Optional, List
from models import Product, ProductCreate, ProductUpdate
from database import database
from bson import ObjectId

class ProductService:
    async def get_products_by_restaurant(self, slug: str, category_id: Optional[str], search: Optional[str], popular_only: bool) -> List[Product]:
        query = {"restaurant_id": slug}
        if category_id:
            query["category_id"] = category_id
        if search:
            query["name"] = {"$regex": search, "$options": "i"}
        if popular_only:
            query["popular"] = True

        products = []
        async for p in database.products.find(query):
            products.append(Product(**p))
        return products

    async def get_product_by_id(self, product_id: str, restaurant_slug: str) -> Optional[Product]:
        product_data = await database.products.find_one({"_id": ObjectId(product_id), "restaurant_id": restaurant_slug})
        if product_data:
            return Product(**product_data)
        return None

    async def create_product(self, slug: str, product_data: ProductCreate) -> Product:
        product = Product(restaurant_id=slug, **product_data.dict())
        await database.products.insert_one(product.dict(by_alias=True))
        return product

    async def update_product(self, product_id: str, product_data: ProductUpdate) -> bool:
        update_result = await database.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": product_data.dict(exclude_unset=True)}
        )
        return update_result.modified_count > 0

    async def delete_product(self, product_id: str) -> bool:
        delete_result = await database.products.delete_one({"_id": ObjectId(product_id)})
        return delete_result.deleted_count > 0
