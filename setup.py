"""
FreshMart Grocery Store - Project Setup Script
Run this once to generate the entire project structure.
Usage: python setup.py
"""

import os

ROOT = os.path.dirname(os.path.abspath(__file__))

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Created: {path}")

print("\n🛒 Setting up FreshMart Grocery Store...\n")

# ─────────────────────────────────────────────
# BACKEND
# ─────────────────────────────────────────────

write("backend/requirements.txt", """\
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
pydantic[email]==2.7.1
""")

write("backend/database.py", """\
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./grocery.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

write("backend/models.py", """\
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    image_url = Column(String)
    stock = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total = Column(Float)
    status = Column(String, default="pending")
    address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
""")

write("backend/schemas.py", """\
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginData(BaseModel):
    email: str
    password: str


class CategoryOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_url: str
    stock: int
    category: Optional[CategoryOut] = None
    model_config = {"from_attributes": True}


class CartItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int
    model_config = {"from_attributes": True}


class AddToCart(BaseModel):
    product_id: int
    quantity: int = 1


class UpdateCart(BaseModel):
    quantity: int


class OrderItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int
    price: float
    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    total: float
    status: str
    address: str
    created_at: datetime
    items: List[OrderItemOut]
    model_config = {"from_attributes": True}


class CreateOrder(BaseModel):
    address: str
""")

write("backend/auth.py", """\
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import models

SECRET_KEY = "grocery-store-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate password to 72 bytes (bcrypt's maximum)
    truncated = plain_password.encode()[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated, hashed_password)


def get_password_hash(password: str) -> str:
    # Truncate password to 72 bytes (bcrypt's maximum)
    truncated = password.encode()[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
""")

write("backend/routers/__init__.py", "")

write("backend/routers/users.py", """\
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(user.password)
    db_user = models.User(name=user.name, email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginData, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user
""")

write("backend/routers/products.py", """\
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
import models
import schemas

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/categories", response_model=List[schemas.CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()


@router.get("", response_model=List[schemas.ProductOut])
def get_products(
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(models.Product)
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    return query.all()


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
""")

write("backend/routers/cart.py", """\
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
from auth import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=List[schemas.CartItemOut])
def get_cart(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()


@router.post("", response_model=schemas.CartItemOut)
def add_to_cart(
    item: schemas.AddToCart,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.product_id == item.product_id,
    ).first()

    if existing:
        existing.quantity += item.quantity
        db.commit()
        db.refresh(existing)
        return existing

    cart_item = models.CartItem(
        user_id=current_user.id,
        product_id=item.product_id,
        quantity=item.quantity,
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.put("/{item_id}", response_model=schemas.CartItemOut)
def update_cart_item(
    item_id: int,
    update: schemas.UpdateCart,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.user_id == current_user.id,
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    cart_item.quantity = update.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item


@router.delete("/{item_id}")
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.user_id == current_user.id,
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed"}


@router.delete("")
def clear_cart(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}
""")

write("backend/routers/orders.py", """\
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
from auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=List[schemas.OrderOut])
def get_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return (
        db.query(models.Order)
        .filter(models.Order.user_id == current_user.id)
        .order_by(models.Order.created_at.desc())
        .all()
    )


@router.post("", response_model=schemas.OrderOut)
def create_order(
    order_data: schemas.CreateOrder,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = sum(item.product.price * item.quantity for item in cart_items)

    order = models.Order(
        user_id=current_user.id,
        total=total,
        address=order_data.address,
        status="confirmed",
    )
    db.add(order)
    db.flush()

    for item in cart_items:
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price,
        )
        db.add(order_item)

    db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).delete()
    db.commit()
    db.refresh(order)
    return order
""")

write("backend/main.py", """\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import users, products, cart, orders

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FreshMart Grocery Store API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/")
def root():
    return {"message": "FreshMart Grocery Store API is running!"}
""")

write("backend/seed.py", """\
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
""")

# ─────────────────────────────────────────────
# FRONTEND
# ─────────────────────────────────────────────

write("frontend/package.json", """\
{
  "name": "freshmart-grocery",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.8",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "react-hot-toast": "^2.4.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "vite": "^5.2.11"
  }
}
""")

write("frontend/vite.config.js", """\
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\\/api/, ''),
      },
    },
  },
})
""")

write("frontend/index.html", """\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>FreshMart - Online Grocery Store</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🛒</text></svg>" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""")

write("frontend/tailwind.config.js", """\
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
""")

write("frontend/postcss.config.js", """\
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
""")

write("frontend/src/index.css", """\
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background-color: #f9fafb;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
""")

write("frontend/src/main.jsx", """\
import React from 'react'
import ReactDOM from 'react-dom/client'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
    <Toaster position="top-right" toastOptions={{ duration: 3000 }} />
  </React.StrictMode>
)
""")

write("frontend/src/App.jsx", """\
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { CartProvider } from './context/CartContext'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Checkout from './pages/Checkout'
import Orders from './pages/Orders'

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <CartProvider>
          <div className="min-h-screen bg-gray-50">
            <Navbar />
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />
              <Route path="/orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
            </Routes>
          </div>
        </CartProvider>
      </AuthProvider>
    </Router>
  )
}
""")

write("frontend/src/api/axios.js", """\
import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
    return Promise.reject(err)
  }
)

export default api
""")

write("frontend/src/context/AuthContext.jsx", """\
import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    const stored = localStorage.getItem('user')
    if (token && stored) {
      try { setUser(JSON.parse(stored)) } catch { localStorage.clear() }
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const res = await api.post('/users/login', { email, password })
    localStorage.setItem('token', res.data.access_token)
    const meRes = await api.get('/users/me')
    localStorage.setItem('user', JSON.stringify(meRes.data))
    setUser(meRes.data)
    return meRes.data
  }

  const register = async (name, email, password) => {
    const res = await api.post('/users/register', { name, email, password })
    return res.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    toast.success('Logged out successfully')
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
""")

write("frontend/src/context/CartContext.jsx", """\
import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api/axios'
import toast from 'react-hot-toast'
import { useAuth } from './AuthContext'

const CartContext = createContext(null)

export function CartProvider({ children }) {
  const [cartItems, setCartItems] = useState([])
  const { user } = useAuth()

  useEffect(() => {
    if (user) fetchCart()
    else setCartItems([])
  }, [user])

  const fetchCart = async () => {
    try {
      const res = await api.get('/cart')
      setCartItems(res.data)
    } catch {}
  }

  const addToCart = async (productId, quantity = 1) => {
    if (!user) { toast.error('Please login to add items'); return }
    try {
      await api.post('/cart', { product_id: productId, quantity })
      await fetchCart()
      toast.success('Added to cart!')
    } catch { toast.error('Failed to add to cart') }
  }

  const updateQuantity = async (itemId, quantity) => {
    if (quantity <= 0) { await removeFromCart(itemId); return }
    try {
      await api.put(`/cart/${itemId}`, { quantity })
      await fetchCart()
    } catch { toast.error('Failed to update') }
  }

  const removeFromCart = async (itemId) => {
    try {
      await api.delete(`/cart/${itemId}`)
      await fetchCart()
      toast.success('Item removed')
    } catch { toast.error('Failed to remove') }
  }

  const clearCart = () => setCartItems([])
  const cartTotal = cartItems.reduce((s, i) => s + i.product.price * i.quantity, 0)
  const cartCount = cartItems.reduce((s, i) => s + i.quantity, 0)

  return (
    <CartContext.Provider value={{ cartItems, addToCart, updateQuantity, removeFromCart, clearCart, cartTotal, cartCount, fetchCart }}>
      {children}
    </CartContext.Provider>
  )
}

export const useCart = () => useContext(CartContext)
""")

write("frontend/src/components/Navbar.jsx", """\
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import Cart from './Cart'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { cartCount } = useCart()
  const [cartOpen, setCartOpen] = useState(false)
  const navigate = useNavigate()

  return (
    <>
      <nav className="bg-green-600 text-white shadow-lg sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold flex items-center gap-2">
            🛒 FreshMart
          </Link>
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-sm hidden sm:block">Hi, {user.name.split(' ')[0]}</span>
                <Link to="/orders" className="text-sm hover:underline hidden sm:block">My Orders</Link>
                <button onClick={logout} className="text-sm hover:underline">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-sm hover:underline">Login</Link>
                <Link to="/register" className="bg-white text-green-600 text-sm font-semibold px-3 py-1.5 rounded-full hover:bg-green-50 transition">
                  Sign Up
                </Link>
              </>
            )}
            <button
              onClick={() => setCartOpen(true)}
              className="relative bg-green-700 hover:bg-green-800 p-2 rounded-full transition"
            >
              🛍️
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                  {cartCount}
                </span>
              )}
            </button>
          </div>
        </div>
      </nav>
      <Cart isOpen={cartOpen} onClose={() => setCartOpen(false)} />
    </>
  )
}
""")

write("frontend/src/components/ProductCard.jsx", """\
import { useCart } from '../context/CartContext'

export default function ProductCard({ product }) {
  const { addToCart } = useCart()

  return (
    <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden border border-gray-100 flex flex-col">
      <div className="h-44 overflow-hidden bg-gray-100">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
          onError={(e) => { e.target.src = `https://placehold.co/400x300?text=${encodeURIComponent(product.name)}` }}
        />
      </div>
      <div className="p-3 flex flex-col flex-1">
        <div className="flex justify-between items-start mb-1 gap-1">
          <h3 className="font-semibold text-gray-800 text-sm leading-tight">{product.name}</h3>
          <span className="text-green-600 font-bold text-sm shrink-0">\${product.price.toFixed(2)}</span>
        </div>
        <p className="text-gray-400 text-xs mb-3 line-clamp-2 flex-1">{product.description}</p>
        <div className="flex items-center justify-between mt-auto">
          <span className={`text-xs ${product.stock > 0 ? 'text-green-500' : 'text-red-400'}`}>
            {product.stock > 0 ? `${product.stock} left` : 'Out of stock'}
          </span>
          <button
            onClick={() => addToCart(product.id)}
            disabled={product.stock === 0}
            className="bg-green-500 hover:bg-green-600 disabled:bg-gray-200 disabled:text-gray-400 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition"
          >
            + Add
          </button>
        </div>
      </div>
    </div>
  )
}
""")

write("frontend/src/components/Cart.jsx", """\
import { useCart } from '../context/CartContext'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Cart({ isOpen, onClose }) {
  const { cartItems, updateQuantity, removeFromCart, cartTotal } = useCart()
  const { user } = useAuth()
  const navigate = useNavigate()

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="flex-1 bg-black bg-opacity-40" onClick={onClose} />
      <div className="w-full max-w-sm bg-white shadow-2xl flex flex-col">
        <div className="p-4 border-b flex justify-between items-center bg-green-600 text-white">
          <h2 className="text-lg font-bold">Your Cart ({cartItems.length} items)</h2>
          <button onClick={onClose} className="text-2xl leading-none hover:opacity-75">×</button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {cartItems.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <div className="text-5xl mb-3">🛒</div>
              <p className="font-medium">Your cart is empty</p>
              <p className="text-sm mt-1">Add some fresh groceries!</p>
            </div>
          ) : (
            cartItems.map(item => (
              <div key={item.id} className="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
                <img
                  src={item.product.image_url}
                  alt={item.product.name}
                  className="w-14 h-14 object-cover rounded-lg shrink-0"
                  onError={(e) => { e.target.src = 'https://placehold.co/56' }}
                />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{item.product.name}</p>
                  <p className="text-green-600 font-semibold text-sm">\${item.product.price.toFixed(2)}</p>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="w-7 h-7 rounded-full bg-gray-200 hover:bg-gray-300 text-sm font-bold flex items-center justify-center">−</button>
                  <span className="w-5 text-center text-sm font-semibold">{item.quantity}</span>
                  <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="w-7 h-7 rounded-full bg-green-500 hover:bg-green-600 text-white text-sm font-bold flex items-center justify-center">+</button>
                </div>
              </div>
            ))
          )}
        </div>

        {cartItems.length > 0 && (
          <div className="p-4 border-t">
            <div className="flex justify-between font-bold text-lg mb-3">
              <span>Total</span>
              <span className="text-green-600">\${cartTotal.toFixed(2)}</span>
            </div>
            <button
              onClick={() => { onClose(); navigate(user ? '/checkout' : '/login') }}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-xl transition"
            >
              {user ? 'Proceed to Checkout →' : 'Login to Checkout'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
""")

write("frontend/src/components/ProtectedRoute.jsx", """\
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-500" />
    </div>
  )
  if (!user) return <Navigate to="/login" replace />
  return children
}
""")

write("frontend/src/pages/Home.jsx", """\
import { useState, useEffect } from 'react'
import api from '../api/axios'
import ProductCard from '../components/ProductCard'

export default function Home() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/products/categories').then(r => setCategories(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams()
    if (selectedCategory) params.append('category_id', selectedCategory)
    if (search) params.append('search', search)
    api.get(`/products?${params}`)
      .then(r => setProducts(r.data))
      .catch(() => setProducts([]))
      .finally(() => setLoading(false))
  }, [selectedCategory, search])

  return (
    <main className="max-w-7xl mx-auto px-4 py-8">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-2xl p-8 mb-8">
        <h1 className="text-3xl md:text-4xl font-bold mb-2">Fresh Groceries Delivered 🥦</h1>
        <p className="text-green-100 text-lg">Shop the freshest produce, dairy, bakery and more.</p>
      </div>

      {/* Search */}
      <div className="mb-5">
        <input
          type="text"
          placeholder="🔍  Search products..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full max-w-lg border border-gray-300 rounded-full px-5 py-3 focus:outline-none focus:ring-2 focus:ring-green-400 shadow-sm text-sm"
        />
      </div>

      {/* Category Filters */}
      <div className="flex gap-2 mb-8 overflow-x-auto pb-1">
        {[{ id: null, name: 'All Products' }, ...categories].map(cat => (
          <button
            key={cat.id ?? 'all'}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition border ${
              selectedCategory === cat.id
                ? 'bg-green-500 text-white border-green-500'
                : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* Products */}
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500" />
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-5xl mb-3">🔍</p>
          <p className="text-lg font-medium">No products found</p>
          <p className="text-sm mt-1">Try a different search or category</p>
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">{products.length} product{products.length !== 1 ? 's' : ''} found</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {products.map(p => <ProductCard key={p.id} product={p} />)}
          </div>
        </>
      )}
    </main>
  )
}
""")

write("frontend/src/pages/Login.jsx", """\
import { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = location.state?.from?.pathname || '/'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password)
      toast.success('Welcome back!')
      navigate(from, { replace: true })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-md">
        <div className="text-center mb-6">
          <div className="text-5xl mb-3">🛒</div>
          <h1 className="text-2xl font-bold text-gray-800">Welcome Back</h1>
          <p className="text-gray-500 text-sm mt-1">Sign in to your FreshMart account</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="email" placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)} required autoFocus
            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400" />
          <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required
            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400" />
          <button type="submit" disabled={loading}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-xl transition disabled:opacity-60">
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="text-center mt-5 text-sm text-gray-500">
          Don't have an account?{' '}
          <Link to="/register" className="text-green-600 font-semibold hover:underline">Sign Up</Link>
        </p>
      </div>
    </div>
  )
}
""")

write("frontend/src/pages/Register.jsx", """\
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 6) { toast.error('Password must be at least 6 characters'); return }
    setLoading(true)
    try {
      await register(form.name, form.email, form.password)
      toast.success('Account created! Please sign in.')
      navigate('/login')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-md">
        <div className="text-center mb-6">
          <div className="text-5xl mb-3">🌿</div>
          <h1 className="text-2xl font-bold text-gray-800">Create Account</h1>
          <p className="text-gray-500 text-sm mt-1">Join FreshMart and shop fresh today</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="text" placeholder="Full name" value={form.name} onChange={set('name')} required autoFocus
            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400" />
          <input type="email" placeholder="Email address" value={form.email} onChange={set('email')} required
            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400" />
          <input type="password" placeholder="Password (min. 6 characters)" value={form.password} onChange={set('password')} required minLength={6}
            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400" />
          <button type="submit" disabled={loading}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-xl transition disabled:opacity-60">
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p className="text-center mt-5 text-sm text-gray-500">
          Already have an account?{' '}
          <Link to="/login" className="text-green-600 font-semibold hover:underline">Sign In</Link>
        </p>
      </div>
    </div>
  )
}
""")

write("frontend/src/pages/Checkout.jsx", """\
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '../context/CartContext'
import api from '../api/axios'
import toast from 'react-hot-toast'

export default function Checkout() {
  const { cartItems, cartTotal, clearCart } = useCart()
  const [address, setAddress] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleOrder = async (e) => {
    e.preventDefault()
    if (!address.trim()) { toast.error('Please enter a delivery address'); return }
    setLoading(true)
    try {
      await api.post('/orders', { address })
      clearCart()
      toast.success('Order placed successfully! 🎉')
      navigate('/orders')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to place order')
    } finally {
      setLoading(false)
    }
  }

  if (cartItems.length === 0) {
    return (
      <div className="max-w-lg mx-auto px-4 py-20 text-center">
        <div className="text-6xl mb-4">🛒</div>
        <h2 className="text-xl font-bold text-gray-700 mb-2">Your cart is empty</h2>
        <button onClick={() => navigate('/')} className="mt-4 bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-xl font-semibold transition">
          Browse Products
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Checkout</h1>
      <div className="grid md:grid-cols-2 gap-8">

        {/* Order Summary */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Order Summary</h2>
          <div className="space-y-3">
            {cartItems.map(item => (
              <div key={item.id} className="flex items-center gap-3 bg-white p-3 rounded-xl border">
                <img src={item.product.image_url} alt={item.product.name} className="w-14 h-14 object-cover rounded-lg"
                  onError={e => { e.target.src = 'https://placehold.co/56' }} />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{item.product.name}</p>
                  <p className="text-gray-400 text-xs">Qty: {item.quantity} × \${item.product.price.toFixed(2)}</p>
                </div>
                <span className="font-bold text-green-600 text-sm shrink-0">
                  \${(item.product.price * item.quantity).toFixed(2)}
                </span>
              </div>
            ))}
          </div>
          <div className="mt-4 p-4 bg-green-50 border border-green-100 rounded-xl">
            <div className="flex justify-between font-bold text-lg">
              <span>Total</span>
              <span className="text-green-600">\${cartTotal.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Delivery Details */}
        <div>
          <h2 className="text-lg font-semibold text-gray-700 mb-4">Delivery Details</h2>
          <form onSubmit={handleOrder} className="bg-white rounded-xl border p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Address</label>
              <textarea
                placeholder="Enter your full delivery address including apartment, city, state and zip code..."
                value={address}
                onChange={e => setAddress(e.target.value)}
                required
                rows={5}
                className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 resize-none"
              />
            </div>
            <button type="submit" disabled={loading}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-xl transition disabled:opacity-60 text-lg">
              {loading ? 'Placing Order...' : `Place Order • \$${cartTotal.toFixed(2)}`}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
""")

write("frontend/src/pages/Orders.jsx", """\
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/axios'

const STATUS_STYLES = {
  confirmed: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  delivered: 'bg-blue-100 text-blue-700',
  cancelled: 'bg-red-100 text-red-700',
}

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/orders')
      .then(r => setOrders(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex justify-center py-20">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500" />
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">My Orders</h1>

      {orders.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <div className="text-6xl mb-4">📦</div>
          <p className="text-xl font-medium mb-2">No orders yet</p>
          <p className="text-sm mb-6">Start shopping to see your orders here</p>
          <Link to="/" className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-xl font-semibold transition">
            Browse Products
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map(order => (
            <div key={order.id} className="bg-white rounded-2xl border shadow-sm overflow-hidden">
              <div className="p-4 bg-gray-50 border-b flex flex-wrap justify-between items-center gap-2">
                <div>
                  <span className="font-bold text-gray-800">Order #{order.id}</span>
                  <span className="text-gray-400 text-sm ml-3">
                    {new Date(order.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-semibold px-3 py-1 rounded-full capitalize ${STATUS_STYLES[order.status] || 'bg-gray-100 text-gray-600'}`}>
                    {order.status}
                  </span>
                  <span className="font-bold text-green-600">\${order.total.toFixed(2)}</span>
                </div>
              </div>
              <div className="p-4">
                <p className="text-sm text-gray-500 mb-3 flex gap-1 items-start">
                  <span>📍</span>
                  <span>{order.address}</span>
                </p>
                <div className="divide-y">
                  {order.items.map(item => (
                    <div key={item.id} className="flex items-center gap-3 py-2">
                      <img src={item.product.image_url} alt={item.product.name} className="w-12 h-12 object-cover rounded-lg shrink-0"
                        onError={e => { e.target.src = 'https://placehold.co/48' }} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{item.product.name}</p>
                        <p className="text-xs text-gray-400">Qty {item.quantity} × \${item.price.toFixed(2)}</p>
                      </div>
                      <span className="text-sm font-semibold text-gray-700 shrink-0">
                        \${(item.quantity * item.price).toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
""")

# ─────────────────────────────────────────────
# README
# ─────────────────────────────────────────────

write("README.md", """\
# 🛒 FreshMart — Grocery Store E-Commerce

A full-stack grocery store web app built with **React**, **FastAPI (Python)**, and **SQLite**.

## Tech Stack
- **Frontend**: React 18 + Vite + Tailwind CSS + React Router v6
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Auth**: JWT tokens (stored in localStorage)

## Features
- Browse products by category or search
- Add/remove items from cart (live badge count)
- Register & login with JWT auth
- Checkout with delivery address
- View order history with status

## Project Structure
```
project/
├── backend/       # FastAPI app
├── frontend/      # React + Vite app
└── README.md
```

## Quick Start

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python seed.py          # Seed DB with 22 sample products
uvicorn main:app --reload
```
API docs → http://localhost:8000/docs

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
App → http://localhost:5173

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /users/register | Register new user |
| POST | /users/login | Login → JWT token |
| GET | /users/me | Current user info |
| GET | /products | List products (filter by category/search) |
| GET | /products/categories | List categories |
| GET | /cart | Get cart (auth required) |
| POST | /cart | Add to cart |
| PUT | /cart/{id} | Update quantity |
| DELETE | /cart/{id} | Remove item |
| GET | /orders | Get my orders |
| POST | /orders | Place order (clears cart) |
""")

print("\n✅ Project created successfully!\n")
print("=" * 50)
print("NEXT STEPS:")
print("=" * 50)
print()
print("1. Start the backend:")
print("   cd backend")
print("   pip install -r requirements.txt")
print("   python seed.py")
print("   uvicorn main:app --reload")
print()
print("2. Start the frontend (new terminal):")
print("   cd frontend")
print("   npm install")
print("   npm run dev")
print()
print("3. Open http://localhost:5173 in your browser")
print()
print("API docs: http://localhost:8000/docs")