from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app.api.endpoints import auth, products, inbound, outbound, users, branches # Import the new branches router

app = FastAPI(
    title="WMS Enterprise API",
    description="Warehouse Management System (WMS) de nível enterprise.",
    version="0.1.0",
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"]) 
app.include_router(branches.router, prefix="/api", tags=["Branches"]) # Add the new branches router
app.include_router(products.router, prefix="/wms", tags=["Products"])
app.include_router(inbound.router, prefix="/wms", tags=["Inbound"])
app.include_router(outbound.router, prefix="/wms", tags=["Outbound"])

@app.get("/", tags=["Root"], summary="Verifica se a API está online")
def read_root():
    """
    Endpoint raiz para verificar o status da API.
    """
    return {"status": "online", "message": "Bem-vindo à WMS Enterprise API!"}
