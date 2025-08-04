from typing import Optional, List
from models import Restaurant, RestaurantCreate, RestaurantUpdate
from database import database

class RestaurantService:
    async def get_by_slug(self, slug: str) -> Optional[Restaurant]:
        restaurant_data = await database.restaurants.find_one({"slug": slug})
        if restaurant_data:
            return Restaurant(**restaurant_data)
        return None

    async def update_restaurant(self, slug: str, restaurant_data: RestaurantUpdate) -> bool:
        update_result = await database.restaurants.update_one(
            {"slug": slug},
            {"$set": restaurant_data.dict(exclude_unset=True)}
        )
        return update_result.modified_count > 0

    async def create_restaurant(self, restaurant_data: RestaurantCreate) -> Restaurant:
        restaurant = Restaurant(**restaurant_data.dict())
        await database.restaurants.insert_one(restaurant.dict(by_alias=True))
        return restaurant

    async def get_all_restaurants(self) -> List[Restaurant]:
        restaurants = []
        async for r in database.restaurants.find({}):
            restaurants.append(Restaurant(**r))
        return restaurants
