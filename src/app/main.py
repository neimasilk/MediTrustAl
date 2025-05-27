from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Added import
from src.app.api.endpoints import users, auth, medical_records, nlp as nlp_router, ai
from src.app.api.api_v1.endpoints import audit_logs # Import the new audit_logs router

# Define allowed origins for CORS
origins = [
    "http://localhost:5173",  # Vite default frontend URL
    "http://localhost:3000",  # Common React development URL
    # Add other origins if necessary, e.g., production frontend URL
]

app = FastAPI(
    title="MediTrustAI API",
    description="API for MediTrustAI blockchain-based user registry",
    version="1.0.0"
)

# Add CORS middleware
# This should be added before any routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all standard methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers with consistent API versioning
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"]) # Corrected tag
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(medical_records.router, prefix="/api/v1/medical-records", tags=["medical-records"])
app.include_router(nlp_router.router, prefix="/api/v1/nlp", tags=["NLP"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Predictive Service"])
app.include_router(audit_logs.router, prefix="/api/v1/audit", tags=["Audit Logs"]) # Added audit_logs router

@app.get("/")
async def root():
    return {"message": "Welcome to MediTrustAI API"} # Corrected typo