
from fastapi import FastAPI, HTTPException
from app.database import test_connection
from app.routers.auth import router as auth_router

app = FastAPI(
    title="Fashion Ecommerce API",
    description="Backend for fashion ecommerce website",
    version="1.0.0"
)

app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "Fashion Ecommerce API is running!"}

@app.get("/health/db")
def check_database():
    try:
        test_connection()
        return {
            "status": "success",
            "message": "Connected to PostgreSQL!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
