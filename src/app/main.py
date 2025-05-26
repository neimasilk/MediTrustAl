from fastapi import FastAPI
from .api.endpoints import users, auth, medical_records

app = FastAPI(
    title="MediTrustAI API",
    description="API for MediTrustAI blockchain-based user registry",
    version="1.0.0"
)

# Include routers with consistent API versioning
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(medical_records.router, prefix="/api/v1/medical-records", tags=["medical-records"])

@app.get("/")
async def root():
    return {"message": "Welcome to MediTrustAl API"}