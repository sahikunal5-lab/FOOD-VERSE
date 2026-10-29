import os
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, get_db_info, init_db
import models  # Registers all SQLAlchemy models with Base.metadata

from routers.database import router as database_router
from routers.food_recognition import router as food_recognition_router
from routers.freshness import router as freshness_router
from routers.hygiene_monitor import router as hygiene_router
from routers.kitchen_assistant import router as kitchen_router
from routers.meal_planner import router as meal_planner_router
from routers.nutrition import router as nutrition_router
from routers.nutrition_scoring import router as nutrition_scoring_router
from services.image_preprocessing import preprocess_food_image

try:
    from routers.food_items import router as food_items_router
except ImportError:
    food_items_router = None

try:
    from routers.food_logs import router as food_logs_router
except ImportError:
    food_logs_router = None

try:
    from routers.meal_plans import router as meal_plans_router
except ImportError:
    meal_plans_router = None

try:
    from routers.recommendations import router as recommendations_router
except ImportError:
    recommendations_router = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan event: initializes database tables and seeds catalog."""
    init_db()
    yield


app = FastAPI(
    title="FoodVerse AI API",
    description=(
        "Full-Stack Food Intelligence, Nutrition Estimation, "
        "and Personalized Meal Planning Backend API."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS Middleware for Frontend Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "*",  # Permissive for local development previews
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
if food_items_router:
    app.include_router(food_items_router)
if recommendations_router:
    app.include_router(recommendations_router)
if meal_plans_router:
    app.include_router(meal_plans_router)
if food_logs_router:
    app.include_router(food_logs_router)
app.include_router(database_router)
app.include_router(meal_planner_router)
app.include_router(nutrition_router)
app.include_router(nutrition_scoring_router)
app.include_router(food_recognition_router)
app.include_router(freshness_router)
app.include_router(hygiene_router)
app.include_router(kitchen_router)


@app.get("/", tags=["General"])
def home():
    """Root endpoint welcoming visitors and providing system status."""
    db_info = get_db_info()
    return {
        "project": "FoodVerse AI",
        "version": "1.0.0",
        "message": "Welcome to FoodVerse AI API!",
        "status": "running",
        "database": db_info,
        "docs_url": "/docs",
    }


@app.get("/health", tags=["General"])
def health_check():
    """Health check endpoint reporting API and database connectivity."""
    db_info = get_db_info()
    return {
        "status": "healthy" if db_info["is_alive"] else "degraded",
        "project": "FoodVerse AI",
        "version": "1.0.0",
        "database": db_info,
    }


@app.post("/image/preprocess", tags=["Image Preprocessing"])
async def preprocess_uploaded_image(file: UploadFile = File(...)):
    """Preprocess an uploaded image and return visual computer vision features."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image file.",
        )

    temp_path = None
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded image is empty.",
            )

        suffix = os.path.splitext(file.filename or "")[1] or ".jpg"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(image_bytes)
            temp_path = temp_file.name

        preprocessed_img, features = preprocess_food_image(temp_path)
        return {
            "success": True,
            "filename": file.filename,
            "features": features,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image preprocessing failed: {exc}",
        ) from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
