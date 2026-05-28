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
