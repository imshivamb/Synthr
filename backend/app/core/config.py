from pydantic_settings import BaseSettings
from typing import List
import secrets

class Settings(BaseSettings):
    PROJECT_NAME: str = "Synthr"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI Agent Marketplace API"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str = None
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend URL
        "http://localhost:8000",  # Backend URL
    ]
    
    # Blockchain
    CONTRACT_ADDRESS: str
    RPC_URL: str
    CHAIN_ID: int
    
    # IPFS
    IPFS_PROJECT_ID: str
    IPFS_PROJECT_SECRET: str
    IPFS_GATEWAY: str
    
    # AI Training
    TRAINING_QUEUE_NAME: str = "training_queue"
    MODEL_STORAGE_PATH: str = "models"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self):
        super().__init__()
        self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

settings = Settings()