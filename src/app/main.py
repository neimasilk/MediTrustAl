from fastapi import FastAPI
from src.app.api.endpoints import users, auth, medical_records, nlp as nlp_router, ai

app = FastAPI(
    title="MediTrustAI API",
    description="API for MediTrustAI blockchain-based user registry",
    version="1.0.0"
)

# Include routers with consistent API versioning
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"]) # Corrected tag
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(medical_records.router, prefix="/api/v1/medical-records", tags=["medical-records"])
app.include_router(nlp_router.router, prefix="/api/v1/nlp", tags=["NLP"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Predictive Service"])

@app.get("/")
async def root():
    return {"message": "Welcome to MediTrustAI API"} # Corrected typo