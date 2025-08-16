#!/usr/bin/env python3
"""
RemotelyX Job Automation Service
Main entry point for the job automation backend service.

Usage:
    python main.py api          # Run as API server
    python main.py scheduler    # Run as scheduled service
    python main.py process      # Run one-time processing
    python main.py test         # Run test mode
"""

import sys
import logging
import argparse
from job_processor import job_processor
from scheduler import job_scheduler
from config import settings, ensure_directories

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_api_server():
    """Run the FastAPI server"""
    try:
        import uvicorn
        from api import app
        
        logger.info("Starting RemotelyX Job Automation API Server")
        logger.info(f"Server will be available at http://{settings.api_host}:{settings.api_port}")
        logger.info(f"API documentation at http://{settings.api_host}:{settings.api_port}/docs")
        
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_level=settings.log_level.lower()
        )
        
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        sys.exit(1)


def run_scheduler():
    """Run the scheduled job processing service"""
    try:
        logger.info("Starting RemotelyX Job Automation Scheduler")
        logger.info(f"Processing interval: {job_scheduler.interval_minutes} minutes")
        logger.info(f"Email limit per run: {job_scheduler.email_limit}")
        
        # Start the scheduler
        job_scheduler.start()
        
        # Keep the main thread alive
        try:
            while True:
                import time
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
            job_scheduler.stop()
            
    except Exception as e:
        logger.error(f"Error running scheduler: {e}")
        sys.exit(1)


def run_one_time_processing():
    """Run one-time job processing"""
    try:
        logger.info("Starting one-time job processing")
        
        # Run the workflow
        result = job_processor.run_full_workflow(email_limit=10)
        
        if result['success']:
            logger.info("One-time processing completed successfully")
            logger.info(f"Jobs processed: {result['jobs_processed']}")
            logger.info(f"Jobs exported: {result['jobs_exported']}")
            logger.info(f"Jobs marked: {result['jobs_marked']}")
            logger.info(f"Duration: {result['duration']:.2f} seconds")
        else:
            logger.error("One-time processing failed")
            logger.error(f"Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error in one-time processing: {e}")
        sys.exit(1)


def run_test_mode():
    """Run in test mode with limited processing"""
    try:
        logger.info("Starting test mode")
        
        # Test database connection
        logger.info("Testing database connection...")
        from database import db_manager
        db_manager.client.admin.command('ping')
        logger.info("✓ Database connection successful")
        
        # Test email connection
        logger.info("Testing email connection...")
        from email_service import email_service
        if email_service.connect():
            logger.info("✓ Email connection successful")
            email_service.disconnect()
        else:
            logger.warning("✗ Email connection failed")
        
        # Test scraper
        logger.info("Testing web scraper...")
        from scraper import job_scraper
        logger.info("✓ Web scraper initialized")
        
        # Test Excel exporter
        logger.info("Testing Excel exporter...")
        from excel_exporter import excel_exporter
        stats = excel_exporter.get_statistics()
        logger.info(f"✓ Excel exporter working - {stats['total_jobs']} jobs in file")
        
        # Run a small test workflow
        logger.info("Running test workflow...")
        result = job_processor.run_full_workflow(email_limit=1)
        
        if result['success']:
            logger.info("✓ Test workflow completed successfully")
        else:
            logger.warning("✗ Test workflow had issues")
        
        logger.info("Test mode completed")
        
    except Exception as e:
        logger.error(f"Error in test mode: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="RemotelyX Job Automation Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py api          # Run as API server
  python main.py scheduler    # Run as scheduled service
  python main.py process      # Run one-time processing
  python main.py test         # Run test mode
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['api', 'scheduler', 'process', 'test'],
        help='Service mode to run'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Processing interval in minutes (for scheduler mode)'
    )
    
    parser.add_argument(
        '--email-limit',
        type=int,
        default=10,
        help='Email limit per processing run'
    )
    
    args = parser.parse_args()
    
    try:
        # Ensure directories exist
        ensure_directories()
        
        # Set configuration
        job_scheduler.set_interval(args.interval)
        job_scheduler.set_email_limit(args.email_limit)
        
        # Run the selected mode
        if args.mode == 'api':
            run_api_server()
        elif args.mode == 'scheduler':
            run_scheduler()
        elif args.mode == 'process':
            run_one_time_processing()
        elif args.mode == 'test':
            run_test_mode()
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        job_processor.cleanup()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        job_processor.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main() 