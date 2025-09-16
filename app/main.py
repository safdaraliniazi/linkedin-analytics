from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, posts, analytics, admin
from app.scheduler import start_scheduler, stop_scheduler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting LinkedIn Analytics Backend...")
    logger.info(f"Database URL: {settings.database_url}")
    await start_scheduler()
    logger.info("Post scheduler started")
    yield
    # Shutdown
    logger.info("Shutting down LinkedIn Analytics Backend...")
    await stop_scheduler()
    logger.info("Post scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    return {
        "message": "LinkedIn Analytics Backend API",
        "version": settings.api_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        from app.database import engine
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.api_version,
            "environment": "production" if "render" in settings.database_url else "development"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
