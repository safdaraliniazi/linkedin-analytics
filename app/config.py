from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/linkedin_analytics",
        env="DATABASE_URL"
    )
    
    # JWT settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # API settings
    api_title: str = Field(default="LinkedIn Analytics Backend", env="API_TITLE")
    api_version: str = Field(default="1.0.0", env="API_VERSION")
    api_description: str = Field(default="Backend system for LinkedIn analytics platform", env="API_DESCRIPTION")
    
    class Config:
        env_file = ".env"


settings = Settings()
