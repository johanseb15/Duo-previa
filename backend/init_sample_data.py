import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from db.mongo import init_db, get_collection
from services.restaurants import RestaurantService
from services.categories import CategoryService
from services.products import ProductService
from models import RestaurantCreate, CategoryCreate, ProductCreate

load_dotenv()

async def init_sample_data():
    """Initialize sample data for DUO Previa"""
    print(" Inicializando datos de DUO Previa")
    
    try:
        # Initialize database connection
        await init_db()
        print("✅ Conexión a base de datos establecida")
        
        # Initialize services
        restaurant_service = RestaurantService()
        category_service = CategoryService()
        product_service = ProductService()
        
        # Check if restaurant already exists
        existing_restaurant = await restaurant_service.get_by_slug("duo-previa")
        if existing_restaurant:
            print("ℹ️  Restaurante DUO Previa ya existe")
            return
        
        # Create DUO Previa restaurant
        restaurant_data = RestaurantCreate(
            name="DUO Previa",
            slug="duo-previa",
            description="Lomitos, hamburguesas y empanadas artesanales en Córdoba",
            logo="",
            email="duo@previa.com.ar",
            phone="+54 351 123-4567",
            address="Av. Colón 123, Centro",
            city="Córdoba",
            country="Argentina",
            admin_username="admin",
            admin_password="admin123"
        )
        
        restaurant = await restaurant_service.create_restaurant(restaurant_data)
        print(f"✅ Restaurante creado: {restaurant.name}")
        
        # Create categories
        categories_data = [
            {"name": " Lomitos", "icon": "", "display_order": 1},
            {"name": " Hamburguesas", "icon": "", "display_order": 2},
            {"name": " Empanadas", "icon": "", "display_order": 3},
            {"name": " Bebidas", "icon": "", "display_order": 4},
            {"name": " Postres", "icon": "", "display_order": 5},
        ]
        
        created_categories = {}
        for cat_data in categories_data:
            category = await category_service.create_category(
                "duo-previa",
                CategoryCreate(**cat_data)
            )
            created_categories[cat_data["name"]] = category.id
            print(f"✅ Categoría creada: {category.name}")
        
        # Create sample products
        products_data = [
            # Lomitos
            {
                "name": "Lomito Completo",
                "description": "Lomito de cerdo con jamón, queso, lechuga, tomate, huevo y papas fritas",
                "price": 4500.0,
                "image": "",
                "category_id": created_categories[" Lomitos"],
                "is_popular": True,
                "preparation_time": 20
            },
            {
                "name": "Lomito Simple",
                "description": "Lomito de cerdo con lechuga y tomate",
                "price": 3200.0,
                "image": "",
                "category_id": created_categories[" Lomitos"],
                "preparation_time": 15
            },
            {
                "name": "Lomito Napolitano",
                "description": "Lomito con jamón, queso, tomate y salsa",
                "price": 4200.0,
                "image": "",
                "category_id": created_categories[" Lomitos"],
                "is_popular": True,
                "preparation_time": 18
            },
            
            # Hamburguesas
            {
                "name": "Hamburguesa DUO",
                "description": "Doble carne, queso cheddar, bacon, cebolla caramelizada",
                "price": 4200.0,
                "image": "",
                "category_id": created_categories[" Hamburguesas"],
                "is_popular": True,
                "preparation_time": 15
            },
            {
                "name": "Hamburguesa Clásica",
                "description": "Carne, queso, lechuga, tomate y cebolla",
                "price": 3500.0,
                "image": "",
                "category_id": created_categories[" Hamburguesas"],
                "preparation_time": 12
            },
            {
                "name": "Hamburguesa Veggie",
                "description": "Medallón vegetal, queso, lechuga, tomate",
                "price": 3200.0,
                "image": "",
                "category_id": created_categories[" Hamburguesas"],
                "is_vegetarian": True,
                "preparation_time": 12
            },
            
            # Empanadas
            {
                "name": "Empanadas de Carne",
                "description": "Empanadas artesanales de carne cortada a cuchillo (x6)",
                "price": 2400.0,
                "image": "",
                "category_id": created_categories[" Empanadas"],
                "is_popular": True,
                "preparation_time": 10
            },
            {
                "name": "Empanadas de Pollo",
                "description": "Empanadas de pollo con verduras (x6)",
                "price": 2200.0,
                "image": "",
                "category_id": created_categories[" Empanadas"],
                "preparation_time": 10
            },
            {
                "name": "Empanadas de Jamón y Queso",
                "description": "Empanadas de jamón y queso (x6)",
                "price": 2000.0,
                "image": "",
                "category_id": created_categories[" Empanadas"],
                "preparation_time": 10
            },
            
            # Bebidas
            {
                "name": "Coca Cola 500ml",
                "description": "Gaseosa Coca Cola 500ml",
                "price": 800.0,
                "image": "",
                "category_id": created_categories[" Bebidas"],
                "preparation_time": 1
            },
            {
                "name": "Agua Mineral 500ml",
                "description": "Agua mineral sin gas 500ml",
                "price": 600.0,
                "image": "",
                "category_id": created_categories[" Bebidas"],
                "preparation_time": 1
            },
            {
                "name": "Cerveza Quilmes 473ml",
                "description": "Cerveza Quilmes lata 473ml",
                "price": 1200.0,
                "image": "",
                "category_id": created_categories[" Bebidas"],
                "preparation_time": 1
            },
            
            # Postres
            {
                "name": "Flan Casero",
                "description": "Flan casero con dulce de leche y crema",
                "price": 1500.0,
                "image": "",
                "category_id": created_categories[" Postres"],
                "preparation_time": 5
            },
            {
                "name": "Helado 1/4kg",
                "description": "Helado artesanal 1/4 kg (sabores varios)",
                "price": 2200.0,
                "image": "",
                "category_id": created_categories[" Postres"],
                "preparation_time": 3
            }
        ]
        
        for product_data in products_data:
            product = await product_service.create_product(
                "duo-previa",
                ProductCreate(**product_data)
            )
            print(f"✅ Producto creado: {product.name}")
        
        print("\n ¡Datos iniciales de DUO Previa creados exitosamente!")
        print("\n Credenciales de acceso:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("   Restaurant slug: duo-previa")
        print("\n URLs de prueba:")
        print("   API: http://localhost:8000")
        print("   Docs: http://localhost:8000/docs")
        print("   Health: http://localhost:8000/health")
        
    except Exception as e:
        print(f"❌ Error inicializando datos: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_sample_data())
