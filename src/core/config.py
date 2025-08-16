"""
Configuration management for RemotelyX Job Automation Service.
Handles environment variables and application settings.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "RemotelyX Job Automation"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Gmail/IMAP Configuration
    gmail_email: Optional[str] = Field(default=None, env="GMAIL_EMAIL")
    gmail_password: Optional[str] = Field(default=None, env="GMAIL_PASSWORD")
    imap_server: str = Field(default="imap.gmail.com", env="IMAP_SERVER")
    imap_port: int = Field(default=993, env="IMAP_PORT")
    
    # Email Filtering
    sender_email: Optional[str] = Field(default=None, env="SENDER_EMAIL")
    subject_filter: str = Field(default="RemotelyX", env="SUBJECT_FILTER")
    
    # MongoDB Configuration
    mongodb_uri: str = Field(default="mongodb://localhost:27017", env="MONGODB_URI")
    mongodb_database: str = Field(default="remotelyx_jobs", env="MONGODB_DATABASE")
    mongodb_collection: str = Field(default="job_postings", env="MONGODB_COLLECTION")
    
    # Excel Export
    excel_file_path: str = Field(default="data/job_postings.xlsx", env="EXCEL_FILE_PATH")
    excel_backup_dir: str = Field(default="data/backups", env="EXCEL_BACKUP_DIR")
    
    # Scraping
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        env="USER_AGENT"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    
    # Scheduler
    scheduler_interval_minutes: int = Field(default=30, env="SCHEDULER_INTERVAL_MINUTES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from environment variables

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            Path(self.log_file).parent,
            Path(self.excel_file_path).parent,
            Path(self.excel_backup_dir),
            Path("data"),
            Path("logs")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings 