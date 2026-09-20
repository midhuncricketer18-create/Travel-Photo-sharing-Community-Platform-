import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app import models

from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.cart import router as cart_router
from app.api.photographers import router as photographer_router
from app.api.photos import router as photo_router
from app.api.products import router as product_router
from app.api.orders import router as order_router


app = FastAPI(title="Online Photography Print Platform API")

Base.metadata.create_all(bind=engine)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(cart_router)
app.include_router(photographer_router)
app.include_router(photo_router)
app.include_router(product_router)
app.include_router(order_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "Online Photography Print Platform API is running"
    }