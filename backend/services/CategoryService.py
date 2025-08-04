from typing import Optional, List
from models import Category, CategoryCreate, CategoryUpdate
from database import database
from bson import ObjectId

class CategoryService:
    async def get_categories_by_restaurant(self, slug: str) -> List[Category]:
        categories = []
        async for c in database.categories.find({"restaurant_id": slug}):
            categories.append(Category(**c))
        return categories

    async def create_category(self, slug: str, category_data: CategoryCreate) -> Category:
        category = Category(restaurant_id=slug, **category_data.dict())
        await database.categories.insert_one(category.dict(by_alias=True))
        return category

    async def update_category(self, category_id: str, category_data: CategoryUpdate) -> bool:
        update_result = await database.categories.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": category_data.dict(exclude_unset=True)}
        )
        return update_result.modified_count > 0

    async def delete_category(self, category_id: str) -> bool:
        delete_result = await database.categories.delete_one({"_id": ObjectId(category_id)})
        return delete_result.deleted_count > 0
