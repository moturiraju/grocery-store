from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import users, products, cart, orders
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FreshMart Grocery Store API", version="1.0.0")

# Allow CORS from development and production frontends
allowed_origins = [
    "http://localhost:5173",  # Local development
    "http://localhost:3000",  # Local development (alternative)
]

# Add production frontend URL if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
