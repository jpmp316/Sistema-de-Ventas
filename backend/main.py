import os

from fastapi import FastAPI
from models import user, product, role, sales  # noqa: F401
from routes import category_routes, user_routes, product_routes, sales_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI Inventory")
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_routes.router)
app.include_router(product_routes.router)
app.include_router(category_routes.router)
app.include_router(sales_routes.router)


