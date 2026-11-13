
from fastapi import FastAPI, HTTPException
from app.database import test_connection
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.middleware.error_handler import register_exception_handlers

app = FastAPI(
    title="Fashion Ecommerce API",
    description="Backend for fashion ecommerce website",
    version="1.0.0"
)

register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(users_router)

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
