"""
Core Configuration Module
Centralized configuration management for Arusha Catholic Seminary
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator, Field
import secrets


class Settings(BaseSettings):
    """Application settings with proper validation and security"""
    
    # Application Information
    APP_NAME: str = "Arusha Catholic Seminary"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment")
    
    # Security Configuration
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="JWT secret key"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiry")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiry")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./arusha_seminary.db",
        description="Database connection URL"
    )
    DATABASE_ECHO: bool = Field(default=False, description="SQL echo mode")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials")
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"],
        description="Allowed HTTP headers"
    )
    
    # File Upload Configuration
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="Max file size (10MB)")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=["jpg", "jpeg", "png", "pdf", "doc", "docx", "xls", "xlsx", "txt"],
        description="Allowed file extensions"
    )
    
    # Email Configuration
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USERNAME: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_TLS: bool = Field(default=True, description="SMTP TLS")
    FROM_EMAIL: str = Field(default="noreply@arushaseminary.com", description="From email")
    FROM_NAME: str = Field(default="Arusha Catholic Seminary", description="From name")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Rate limit per hour")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Log level")
    LOG_FILE: str = Field(default="logs/app.log", description="Log file path")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    LOG_MAX_SIZE: int = Field(default=10 * 1024 * 1024, description="Log max size (10MB)")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Log backup count")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="Default page size")
    MAX_PAGE_SIZE: int = Field(default=100, description="Maximum page size")
    
    # Session Configuration
    SESSION_TIMEOUT: int = Field(default=3600, description="Session timeout (seconds)")
    
    # Backup Configuration
    BACKUP_DIR: str = Field(default="backups", description="Backup directory")
    BACKUP_RETENTION_DAYS: int = Field(default=30, description="Backup retention days")
    
    # Monitoring Configuration
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics")
    METRICS_PORT: int = Field(default=9090, description="Metrics port")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Health check interval")
    
    # Alert Configuration
    ALERT_EMAIL: str = Field(default="admin@arushaseminary.edu", description="Alert email")
    ALERT_RESPONSE_TIME_THRESHOLD: int = Field(default=2000, description="Response time threshold (ms)")
    ALERT_ERROR_RATE_THRESHOLD: float = Field(default=5.0, description="Error rate threshold (%)")
    
    # Validation Methods
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def assemble_allowed_extensions(cls, v):
        if isinstance(v, str):
            return [i.strip().lower() for i in v.split(",")]
        return v
    
    @property
    def database_url(self) -> str:
        """Get database URL with proper formatting"""
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL
        return self.DATABASE_URL
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT.lower() in ["development", "dev"]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT.lower() in ["production", "prod"]
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.ENVIRONMENT.lower() in ["testing", "test"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True


# Environment-specific settings
class DevelopmentSettings(Settings):
    """Development environment settings"""
    DEBUG: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"]


class ProductionSettings(Settings):
    """Production environment settings"""
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "WARNING"
    CORS_ORIGINS: List[str] = ["https://arushaseminary.com", "https://www.arushaseminary.com"]


class TestingSettings(Settings):
    """Testing environment settings"""
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "ERROR"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]


def get_settings() -> Settings:
    """Get application settings based on environment"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment in ["production", "prod"]:
        return ProductionSettings()
    elif environment in ["testing", "test"]:
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()
