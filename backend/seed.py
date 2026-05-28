from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Clear existing data
db.query(models.OrderItem).delete()
db.query(models.Order).delete()
db.query(models.CartItem).delete()
db.query(models.Product).delete()
db.query(models.Category).delete()
db.commit()

categories = [
    models.Category(name="Fruits & Vegetables"),
    models.Category(name="Dairy & Eggs"),
    models.Category(name="Bakery"),
    models.Category(name="Beverages"),
    models.Category(name="Snacks"),
    models.Category(name="Meat & Seafood"),
]
db.add_all(categories)
db.commit()

cat = {c.name: c.id for c in db.query(models.Category).all()}

products = [
    # Fruits & Vegetables
    models.Product(name="Fresh Apples", description="Crisp and sweet red apples, perfect for snacking", price=2.99, image_url="https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400", stock=100, category_id=cat["Fruits & Vegetables"]),
    models.Product(name="Bananas", description="Ripe yellow bananas, rich in potassium", price=1.49, image_url="https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400", stock=150, category_id=cat["Fruits & Vegetables"]),
    models.Product(name="Broccoli", description="Fresh green broccoli, packed with vitamins", price=1.99, image_url="https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=400", stock=80, category_id=cat["Fruits & Vegetables"]),
    models.Product(name="Tomatoes", description="Vine-ripened tomatoes, great for salads", price=2.49, image_url="https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400", stock=120, category_id=cat["Fruits & Vegetables"]),
    models.Product(name="Carrots", description="Crunchy orange carrots, great raw or cooked", price=1.29, image_url="https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400", stock=90, category_id=cat["Fruits & Vegetables"]),
    models.Product(name="Baby Spinach", description="Tender baby spinach leaves, nutritious and fresh", price=2.79, image_url="https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400", stock=60, category_id=cat["Fruits & Vegetables"]),
    # Dairy & Eggs
    models.Product(name="Whole Milk", description="Fresh whole milk, 1 gallon", price=3.99, image_url="https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400", stock=70, category_id=cat["Dairy & Eggs"]),
    models.Product(name="Cheddar Cheese", description="Sharp cheddar cheese block, 16oz", price=5.49, image_url="https://images.unsplash.com/photo-1618164436241-4473940d1f5c?w=400", stock=50, category_id=cat["Dairy & Eggs"]),
    models.Product(name="Free-Range Eggs", description="Free-range large brown eggs, dozen", price=4.99, image_url="https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400", stock=100, category_id=cat["Dairy & Eggs"]),
    models.Product(name="Greek Yogurt", description="Creamy plain Greek yogurt, 32oz", price=6.29, image_url="https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400", stock=45, category_id=cat["Dairy & Eggs"]),
    # Bakery
    models.Product(name="Sourdough Bread", description="Freshly baked artisan sourdough loaf", price=4.49, image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", stock=30, category_id=cat["Bakery"]),
    models.Product(name="Blueberry Muffins", description="Soft muffins loaded with fresh blueberries, pack of 4", price=3.99, image_url="https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400", stock=25, category_id=cat["Bakery"]),
    models.Product(name="Croissants", description="Buttery flaky croissants, pack of 4", price=5.99, image_url="https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=400", stock=20, category_id=cat["Bakery"]),
    # Beverages
    models.Product(name="Orange Juice", description="100% fresh-squeezed orange juice, 64oz", price=5.99, image_url="https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400", stock=55, category_id=cat["Beverages"]),
    models.Product(name="Green Tea", description="Organic green tea bags, 20 count", price=4.29, image_url="https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400", stock=80, category_id=cat["Beverages"]),
    models.Product(name="Sparkling Water", description="Natural sparkling mineral water, 12-pack", price=7.99, image_url="https://images.unsplash.com/photo-1523362628745-0c100150b504?w=400", stock=60, category_id=cat["Beverages"]),
    # Snacks
    models.Product(name="Mixed Nuts", description="Deluxe mixed nuts, no peanuts, 16oz", price=8.99, image_url="https://images.unsplash.com/photo-1559181567-c3190bfbf6b3?w=400", stock=40, category_id=cat["Snacks"]),
    models.Product(name="Kettle Chips", description="Classic salted kettle chips, family size", price=4.49, image_url="https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400", stock=75, category_id=cat["Snacks"]),
    models.Product(name="Dark Chocolate", description="70% dark chocolate bar, 3.5oz", price=3.99, image_url="https://images.unsplash.com/photo-1606312619070-d48b4c652a52?w=400", stock=65, category_id=cat["Snacks"]),
    # Meat & Seafood
    models.Product(name="Chicken Breast", description="Boneless skinless chicken breasts, 2lbs", price=9.99, image_url="https://images.unsplash.com/photo-1604503468506-a8da13d11d36?w=400", stock=35, category_id=cat["Meat & Seafood"]),
    models.Product(name="Atlantic Salmon", description="Wild-caught Atlantic salmon fillet, 1lb", price=12.99, image_url="https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6?w=400", stock=25, category_id=cat["Meat & Seafood"]),
    models.Product(name="Lean Ground Beef", description="Ground beef 90/10 lean, 1lb", price=7.99, image_url="https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400", stock=45, category_id=cat["Meat & Seafood"]),
]
db.add_all(products)
db.commit()
db.close()
print("✅ Database seeded with 22 products across 6 categories!")
