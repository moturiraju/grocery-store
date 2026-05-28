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
