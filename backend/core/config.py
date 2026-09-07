"""
PharmaPack QV — Core Configuration & Settings
"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = "PharmaPack QV"
    APP_VERSION: str = "1.0.0-rc1"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Security & Authentication
    SECRET_KEY: str = "pharmapack-super-secret-key-for-gdp-compliance-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8-hour shift length
    
    # Database
    # Defaults to async SQLite for immediate local execution, seamlessly upgradable to PostgreSQL
    DATABASE_URL: str = f"sqlite+aiosqlite:///{PROJECT_ROOT}/pharmapack.db"
    SYNC_DATABASE_URL: str = f"sqlite:///{PROJECT_ROOT}/pharmapack.db"
    
    # Storage Paths
    DATA_DIR: Path = PROJECT_ROOT / "data"
    SAMPLES_DIR: Path = PROJECT_ROOT / "data" / "samples"
    AUDIT_STORE_DIR: Path = PROJECT_ROOT / "data" / "audit_store"
    
    # Controlled Storage Zones
    ZONE_COLD_CHAIN: str = "2-8°C"
    ZONE_CONTROLLED_ROOM: str = "15-25°C"
    ZONE_FROZEN: str = "-20°C"
    
    # Quality Verification Thresholds
    CONFIDENCE_AUTO_PASS_MIN: float = 0.85
    CONFIDENCE_HITL_ESCALATION_MIN: float = 0.60
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Roboflow Serverless Workflows
    ROBOFLOW_API_KEY: str = "Sye7Ost12vjGImgRoF75"
    ROBOFLOW_WORKSPACE: str = "partha-bnqgk"
    ROBOFLOW_WORKFLOW: str = "pharmapack-damage-detection"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=str(PROJECT_ROOT / ".env"),
        extra="ignore"
    )

settings = Settings()

# Ensure data directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIT_STORE_DIR.mkdir(parents=True, exist_ok=True)
