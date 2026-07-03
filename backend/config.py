import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and configuration environment mapping.
    Loads variables from backend/.env regardless of the working directory,
    and automatically initializes the required local application paths.
    """
    # Application Deployment Environment
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False

    # AI Model Credentials
    GEMINI_API_KEY: str

    # Storage Paths
    UPLOAD_DIR: Path = Path("uploads")
    CHROMA_DB_DIR: Path = Path("chroma_db")

    # Security Configuration
    # Security Configuration - Updated to list the standard Vite development ports as core defaults
    ALLOWED_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Application Logging Configurations
    LOG_LEVEL: str = "INFO"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "1 week"

    # Configuration for pydantic-settings to find backend/.env explicitly
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            Path(__file__).resolve().parent, ".env"
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parses a comma-separated CORS string into a clean list of origins."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    def create_required_directories(self) -> None:
        """
        Ensures all runtime storage and tracking directories exist.
        Guarantees compatibility across Windows and Linux.
        """
        # Ensure paths are resolved correctly relative to current execution context
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)


# Instantiate settings globally for singleton usage throughout the application
settings = Settings()
settings.create_required_directories()