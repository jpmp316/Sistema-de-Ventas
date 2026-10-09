import os
from fastapi import FastAPI
from core.database import Base, engine
from models import user, product  # noqa: F401
from routes import user_routes, product_routes
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI(title="FastAPI Inventory")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_routes.router)
app.include_router(product_routes.router)


