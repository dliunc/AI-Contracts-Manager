from pydantic_settings import BaseSettings
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    MONGODB_URL: str
    DB_NAME: str
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    JWT_SECRET: str = "your-super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    OPENAI_API_KEY: str
    
    # Email configuration
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    class Config:
        env_file = ".env"
    
    def validate_email_config(self) -> bool:
        """Validate email configuration and log status."""
        if not self.ENABLE_EMAIL_NOTIFICATIONS:
            logger.info("Email notifications are disabled")
            return True
            
        missing_fields = []
        if not self.SMTP_SERVER or self.SMTP_SERVER == "smtp.example.com":
            missing_fields.append("SMTP_SERVER")
        if not self.SMTP_USER:
            missing_fields.append("SMTP_USER")
        if not self.SMTP_PASSWORD:
            missing_fields.append("SMTP_PASSWORD")
            
        if missing_fields:
            logger.warning(f"Email notifications enabled but missing configuration: {', '.join(missing_fields)}")
            logger.warning("Email notifications will be disabled until proper configuration is provided")
            return False
        else:
            logger.info(f"Email notifications configured with SMTP server: {self.SMTP_SERVER}")
            return True

@lru_cache()
def get_settings():
    settings_instance = Settings()
    # Validate email configuration on startup
    settings_instance.validate_email_config()
    return settings_instance

settings = get_settings()