#!/usr/bin/env python3
"""
Test script for RemotelyX Job Automation Service
This script tests the basic setup and configuration.
"""

import os
import sys
import logging
from datetime import datetime

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_environment():
    """Test environment variables"""
    logger.info("Testing environment variables...")
    
    required_vars = [
        'GMAIL_EMAIL',
        'GMAIL_PASSWORD', 
        'SENDER_EMAIL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.info("Please set these variables in your .env file")
        return False
    
    logger.info("✓ Environment variables configured")
    return True


def test_imports():
    """Test module imports"""
    logger.info("Testing module imports...")
    
    try:
        import config
        import models
        import database
        import email_service
        import scraper
        import excel_exporter
        import job_processor
        import api
        import scheduler
        
        logger.info("✓ All modules imported successfully")
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    logger.info("Testing configuration...")
    
    try:
        from config import settings
        
        # Test basic settings
        assert settings.gmail_email, "Gmail email not configured"
        assert settings.gmail_password, "Gmail password not configured"
        assert settings.sender_email, "Sender email not configured"
        
        logger.info("✓ Configuration loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        return False


def test_directories():
    """Test directory creation"""
    logger.info("Testing directory creation...")
    
    try:
        from config import ensure_directories
        
        ensure_directories()
        
        # Check if directories exist
        data_dir = os.path.dirname('./data/remotelyx_jobs.xlsx')
        logs_dir = os.path.dirname('./logs/remotelyx.log')
        
        if os.path.exists(data_dir):
            logger.info("✓ Data directory created")
        else:
            logger.warning("✗ Data directory not created")
        
        if os.path.exists(logs_dir):
            logger.info("✓ Logs directory created")
        else:
            logger.warning("✗ Logs directory not created")
        
        return True
        
    except Exception as e:
        logger.error(f"Directory creation error: {e}")
        return False


def test_database_connection():
    """Test database connection"""
    logger.info("Testing database connection...")
    
    try:
        from database import db_manager
        
        # Test connection
        db_manager.client.admin.command('ping')
        logger.info("✓ Database connection successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        logger.info("Make sure MongoDB is running and accessible")
        return False


def test_email_connection():
    """Test email connection"""
    logger.info("Testing email connection...")
    
    try:
        from email_service import email_service
        
        if email_service.connect():
            logger.info("✓ Email connection successful")
            email_service.disconnect()
            return True
        else:
            logger.error("✗ Email connection failed")
            return False
            
    except Exception as e:
        logger.error(f"Email connection error: {e}")
        return False


def test_web_scraper():
    """Test web scraper"""
    logger.info("Testing web scraper...")
    
    try:
        from scraper import job_scraper
        
        # Test with a simple URL
        test_url = "https://httpbin.org/html"
        response = job_scraper._make_request(test_url)
        
        if response and response.status_code == 200:
            logger.info("✓ Web scraper working")
            return True
        else:
            logger.error("✗ Web scraper failed")
            return False
            
    except Exception as e:
        logger.error(f"Web scraper error: {e}")
        return False


def test_excel_exporter():
    """Test Excel exporter"""
    logger.info("Testing Excel exporter...")
    
    try:
        from excel_exporter import excel_exporter
        
        # Test statistics
        stats = excel_exporter.get_statistics()
        logger.info(f"✓ Excel exporter working - {stats['total_jobs']} jobs in file")
        return True
        
    except Exception as e:
        logger.error(f"Excel exporter error: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("Starting RemotelyX Job Automation Service tests...")
    logger.info(f"Test run at: {datetime.now()}")
    
    tests = [
        ("Environment Variables", test_environment),
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Directories", test_directories),
        ("Database Connection", test_database_connection),
        ("Email Connection", test_email_connection),
        ("Web Scraper", test_web_scraper),
        ("Excel Exporter", test_excel_exporter),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            logger.error(f"✗ {test_name} ERROR: {e}")
    
    logger.info(f"\n--- Test Results ---")
    logger.info(f"Passed: {passed}/{total}")
    logger.info(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! The service is ready to use.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 