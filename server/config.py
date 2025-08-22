import os
from typing import Optional

class Settings:
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost:5432/nazarriya"
    )
    
    # JWT settings (we'll use these later)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # App settings
    APP_NAME: str = "NazarRiya Backend"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()
