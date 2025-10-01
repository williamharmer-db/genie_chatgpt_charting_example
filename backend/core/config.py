"""
Configuration module for Genie to Chart POC
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Databricks Configuration
    databricks_host: Optional[str] = Field(default=None, env="GENIE_DATABRICKS_HOST")
    databricks_token: Optional[str] = Field(default=None, env="GENIE_DATABRICKS_TOKEN")
    genie_space_id: Optional[str] = Field(default=None, env="GENIE_SPACE_ID")
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")
    azure_openai_deployment: str = Field(..., env="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str = Field(default="2024-02-01", env="AZURE_OPENAI_API_VERSION")
    
    # Rate Limiting Configuration
    max_retries: int = Field(default=5, env="MAX_RETRIES")
    initial_backoff: float = Field(default=1.0, env="INITIAL_BACKOFF")
    max_backoff: float = Field(default=60.0, env="MAX_BACKOFF")
    backoff_multiplier: float = Field(default=2.0, env="BACKOFF_MULTIPLIER")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

