from fastapi import FastAPI
from .api.endpoints import users

app = FastAPI(
    title="MediTrustAI API",
    description="API for MediTrustAI blockchain-based user registry",
    version="1.0.0"
)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/")
async def root():
    return {"message": "Welcome to MediTrustAl API"}