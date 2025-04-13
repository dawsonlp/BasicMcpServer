"""
Configuration module for the MCP server.

This module handles loading and validating environment variables using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Server settings and configuration loaded from environment variables.
    
    Environment variables can be set directly or loaded from a .env file.
    """
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 7500
    
    # Add your API keys and credentials here
    api_key: str
    other_secret: str = ""  # Optional, has default empty value
    
    # Optional: Add database credentials, etc.
    
    # Configure settings to load from .env file
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Create a settings instance for importing in other modules
settings = Settings()
