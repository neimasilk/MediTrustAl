from fastapi import FastAPI
from app.api import status_routes # Tambahkan ini

app = FastAPI(title="MediTrustAl API", version="0.1.0")

app.include_router(status_routes.router, prefix="/api/v1") # Tambahkan ini

@app.get("/")
async def root():
    return {"message": "Welcome to MediTrustAl API"}