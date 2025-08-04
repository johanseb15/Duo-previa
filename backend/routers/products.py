from fastapi import APIRouter, Body, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List

from ..models import Product, ProductBase, ProductUpdate, TokenData # Importar TokenData
from ..database import database # Importar la instancia de la base de datos
from ..auth import get_current_user # Importar la dependencia de autenticación

router = APIRouter(
    prefix="/api/{restaurant_slug}/products",
    tags=["Products"],
)

@router.get("/", response_model=List[Product])
async def get_products(restaurant_slug: str):
    """
    Obtiene todos los productos de un restaurante específico.
    """
    if database is None:
        # Fallback a datos en memoria si la conexión a la DB falló
        from ..database import db_products
        products = [p for p in db_products.values() if p.restaurant_id == restaurant_slug]
        return products

    products_cursor = database.products.find({"restaurant_id": restaurant_slug})
    products = []
    async for product in products_cursor:
        products.append(Product(**product))
    return products

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(restaurant_slug: str, product_data: ProductBase = Body(...), current_user: TokenData = Depends(get_current_user)):
    """
    Crea un nuevo producto. Ruta protegida por autenticación.
    """
    if current_user.restaurant_id != restaurant_slug:
        raise HTTPException(status_code=403, detail="Not authorized for this restaurant")

    if database is None:
        # Fallback a datos en memoria
        from ..database import db_products
        new_id = str(len(db_products) + 1)
        product = Product(id=new_id, restaurant_id=restaurant_slug, **product_data.dict())
        db_products[new_id] = product
        return product

    product = Product(restaurant_id=restaurant_slug, **product_data.dict())
    product.id = str(product.id) # Asegurarse de que el ID sea string para MongoDB
    new_product = await database.products.insert_one(product.dict(by_alias=True))
    created_product = await database.products.find_one({"_id": new_product.inserted_id})
    return Product(**created_product)

@router.put("/{product_id}", response_model=Product)
async def update_product(restaurant_slug: str, product_id: str, product_update: ProductUpdate = Body(...), current_user: TokenData = Depends(get_current_user)):
    """
    Actualiza un producto existente. Ruta protegida.
    """
    if current_user.restaurant_id != restaurant_slug:
        raise HTTPException(status_code=403, detail="Not authorized for this restaurant")

    if database is None:
        # Fallback a datos en memoria
        from ..database import db_products
        if product_id not in db_products or db_products[product_id].restaurant_id != restaurant_slug:
            raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found in this restaurant")
        stored_product_data = db_products[product_id]
        update_data = product_update.dict(exclude_unset=True)
        updated_product = stored_product_data.copy(update=update_data)
        db_products[product_id] = updated_product
        return updated_product

    # Convertir product_id a ObjectId si es necesario
    from bson import ObjectId
    try:
        obj_id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    existing_product = await database.products.find_one({"_id": obj_id, "restaurant_id": restaurant_slug})
    if existing_product is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found in this restaurant")

    update_data = {k: v for k, v in product_update.dict(exclude_unset=True).items() if v is not None}
    if len(update_data) >= 1:
        await database.products.update_one({"_id": obj_id}, {"$set": update_data})
        updated_product = await database.products.find_one({"_id": obj_id})
        return Product(**updated_product)
    
    # Si no hay datos para actualizar, devuelve el producto existente
    return Product(**existing_product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(restaurant_slug: str, product_id: str, current_user: TokenData = Depends(get_current_user)):
    """
    Elimina un producto. Ruta protegida.
    """
    if current_user.restaurant_id != restaurant_slug:
        raise HTTPException(status_code=403, detail="Not authorized for this restaurant")

    if database is None:
        # Fallback a datos en memoria
        from ..database import db_products
        if product_id in db_products and db_products[product_id].restaurant_id == restaurant_slug:
            del db_products[product_id]
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")

    from bson import ObjectId
    try:
        obj_id = ObjectId(product_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    delete_result = await database.products.delete_one({"_id": obj_id, "restaurant_id": restaurant_slug})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    
    raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
