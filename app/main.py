from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Import all routers
from app.api.endpoints import (
    auth, products, inbound, outbound, users, branches, quality
)

app = FastAPI(
    title="WMS Enterprise API",
    description="Warehouse Management System (WMS) for quality control and stock management.",
    version="0.2.0",
)

# Include routers with appropriate prefixes and tags
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(branches.router, prefix="/api", tags=["Branches"])
app.include_router(quality.router, prefix="/api", tags=["Quality Control"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(inbound.router, prefix="/wms", tags=["Inbound Operations"])
app.include_router(outbound.router, prefix="/wms", tags=["Outbound Operations"])

@app.get("/", tags=["Root"], summary="Check if the API is online")
def read_root():
    """
    Root endpoint to check the API status.
    """
    return {"status": "online", "message": "Welcome to the WMS Enterprise API!"}
