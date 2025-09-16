from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    database_url: str = "postgresql://user:password@localhost:5432/linkedin_analytics"
    
    # JWT settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API settings
    api_title: str = "LinkedIn Analytics Backend"
    api_version: str = "1.0.0"
    api_description: str = "Backend system for LinkedIn analytics platform"
    
    class Config:
        env_file = ".env"


settings = Settings()
