import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator
import secrets


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Arusha Catholic Seminary"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./arusha_seminary.db"
    DATABASE_ECHO: bool = False
    
    # Redis settings (for caching and sessions)
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf,doc,docx,xls,xlsx,txt"
    ENABLE_FILE_SCANNING: bool = True
    FILE_STORAGE_BACKEND: str = "local"  # local, s3, gcs
    
    # Email settings
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    FROM_EMAIL: str = "noreply@arushaseminary.com"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Session settings
    SESSION_TIMEOUT: int = 3600  # 1 hour
    
    # Backup settings
    BACKUP_DIR: str = "backups"
    BACKUP_RETENTION_DAYS: int = 30
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL: int = 30
    ALERT_EMAIL: str = "admin@arushaseminary.edu"
    
    # Logging Configuration
    LOG_FORMAT: str = "json"
    ENABLE_REQUEST_TRACING: bool = True
    ENABLE_PERFORMANCE_LOGGING: bool = True
    
    # Alerting Configuration
    ALERT_RESPONSE_TIME_THRESHOLD: int = 2000  # milliseconds
    ALERT_ERROR_RATE_THRESHOLD: float = 5.0  # percentage
    ALERT_DISK_USAGE_THRESHOLD: float = 80.0  # percentage
    ALERT_MEMORY_USAGE_THRESHOLD: float = 85.0  # percentage
    
    # Phase 4: Advanced Features Configuration

    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@arushaseminary.edu"
    EMAIL_FROM_NAME: str = "Arusha Catholic Seminary"
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    EMAIL_RATE_LIMIT: int = 100  # emails per hour

    # Report Configuration
    REPORT_CACHE_TTL: int = 3600  # 1 hour
    PDF_TEMPLATE_DIR: str = "templates/reports"
    ENABLE_REPORT_GENERATION: bool = True
    REPORT_BACKGROUND_PROCESSING: bool = True

    # Search Configuration
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    SEARCH_INDEX_PREFIX: str = "arusha_seminary"
    ENABLE_FULL_TEXT_SEARCH: bool = True
    SEARCH_RESULT_LIMIT: int = 50

    # Calendar Configuration
    CALENDAR_TIMEZONE: str = "Africa/Dar_es_Salaam"
    ENABLE_CALENDAR_INTEGRATION: bool = True
    CALENDAR_SYNC_INTERVAL: int = 300  # 5 minutes

    # Data Export Configuration
    EXPORT_MAX_RECORDS: int = 10000
    EXPORT_FORMATS: str = "csv,xlsx,pdf"
    EXPORT_CACHE_TTL: int = 1800  # 30 minutes
    ENABLE_BATCH_EXPORT: bool = True
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def assemble_allowed_extensions(cls, v):
        if isinstance(v, str):
            return v
        elif isinstance(v, list):
            return ",".join(v)
        raise ValueError(v)
    
    @property
    def database_url(self) -> str:
        """Get database URL with proper formatting"""
        if self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL
        return self.DATABASE_URL
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL with proper formatting"""
        if self.REDIS_URL:
            return self.REDIS_URL
        
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.DEBUG
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Environment-specific configurations
def get_settings() -> Settings:
    """Get settings based on environment"""
    return settings


# Development settings
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


# Production settings
class ProductionSettings(Settings):
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "WARNING"
    CORS_ORIGINS: List[str] = ["https://arushaseminary.com", "https://www.arushaseminary.com"]


# Testing settings
class TestingSettings(Settings):
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "ERROR"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]


# Get appropriate settings based on environment
def get_environment_settings() -> Settings:
    """Get settings based on environment variable"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Export the main settings instance
__all__ = ["settings", "get_settings", "get_environment_settings"] 