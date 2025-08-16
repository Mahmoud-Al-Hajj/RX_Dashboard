from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Gmail/IMAP Configuration
    gmail_email: str
    gmail_password: str
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    
    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "remotelyx_jobs"
    mongodb_collection: str = "job_postings"
    
    # Email Filtering
    sender_email: str
    subject_keyword: str = "RemotelyX"
    
    # File Paths
    excel_file_path: str = "./data/remotelyx_jobs.xlsx"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/remotelyx.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()


def ensure_directories():
    """Ensure necessary directories exist"""
    os.makedirs(os.path.dirname(settings.excel_file_path), exist_ok=True)
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True) 