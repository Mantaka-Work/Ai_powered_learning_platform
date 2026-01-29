"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.routes import auth, materials, search, generate, chat, validation, health
from app.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    yield
    # Shutdown
    print("👋 Application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Supplementary Learning Platform for University Courses",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(materials.router, prefix="/api/materials", tags=["Materials"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(generate.router, prefix="/api/generate", tags=["Generation"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(validation.router, prefix="/api/validate", tags=["Validation"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
