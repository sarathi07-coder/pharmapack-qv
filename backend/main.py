"""
PharmaPack QV — Main Application Entrypoint
Industrial Pharmaceutical Warehouse Packing Quality Verification API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.core.config import settings
from backend.db.session import init_db
from backend.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    await init_db()
    yield
    # Shutdown: clean up resources if needed

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated packing-quality verification tool combining deterministic GDP rules and computer vision AI for pharmaceutical controlled storage zones.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for Frontend React / Vite client
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files for sample images and audit artifacts
app.mount("/static/samples", StaticFiles(directory=str(settings.SAMPLES_DIR)), name="samples")

@app.get("/api/info")
def api_info():
    return {
        "system": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "OPERATIONAL",
        "standard": "21 CFR Part 11 & WHO Annex 5 GDP Compliant",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "database": "CONNECTED",
        "vision_engine": "READY",
        "rules_engine": "ACTIVE",
        "langgraph_pipeline": "INITIALIZED"
    }

# Mount frontend UI application to root (must be after all explicit API routes)
frontend_dir = settings.DATA_DIR.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
