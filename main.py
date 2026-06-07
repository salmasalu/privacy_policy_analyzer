from fastapi import FastAPI
from app.db.database import engine
from app.db import models
from api.routes import router

# Create all DB tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Privacy Policy Analyzer API",
    description="AI-powered privacy policy risk detection with clause-level explainability, MLOps monitoring, and PostgreSQL-backed analysis history.",
    version="2.0.0"
)

# Register all routes
app.include_router(router)

# Health check
@app.get("/")
def home():
    return {"message": "Privacy Policy Analyzer API is running!"}