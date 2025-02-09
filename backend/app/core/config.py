from pydantic_settings import BaseSettings
from typing import List, Optional
import secrets
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "SYNTHR"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    DEBUG: bool = False
    APP_ENV: str = "development"
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5436"
    DATABASE_URL: str | None = None

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Blockchain Settings
    CONTRACT_ADDRESS: str | None = None
    RPC_URL: str | None = None
    CHAIN_ID: int | None = None

    # IPFS Settings
    IPFS_PROJECT_ID: str | None = None
    IPFS_PROJECT_SECRET: str | None = None
    IPFS_GATEWAY: str | None = None

    # Redis Settings (Optional)
    REDIS_URL: str | None = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    PINATA_API_KEY: str
    PINATA_SECRET_KEY: str
    PINATA_GATEWAY_URL: Optional[str] = "https://gateway.pinata.cloud/ipfs/"

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Construct DATABASE_URL if not provided
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )

        # Construct REDIS_URL if not provided
        if not self.REDIS_URL and self.REDIS_HOST:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()