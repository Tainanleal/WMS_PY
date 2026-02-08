from fastapi import FastAPI

app = FastAPI(
    title="WMS Enterprise API",
    description="Warehouse Management System (WMS) de nível enterprise.",
    version="0.1.0",
)

@app.get("/", tags=["Root"], summary="Verifica se a API está online")
def read_root():
    """
    Endpoint raiz para verificar o status da API.
    """
    return {"status": "online", "message": "Bem-vindo à WMS Enterprise API!"}
