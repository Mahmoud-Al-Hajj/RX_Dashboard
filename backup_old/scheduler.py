import schedule
import time
import logging
import threading
from datetime import datetime
from job_processor import job_processor
from config import settings

logger = logging.getLogger(__name__)


class JobScheduler:
    def __init__(self):
        self.running = False
        self.scheduler_thread = None
        self.interval_minutes = 30  # Default interval
        self.email_limit = 10  # Default email limit
    
    def set_interval(self, minutes: int):
        """Set the interval for job processing"""
        self.interval_minutes = max(1, minutes)  # Minimum 1 minute
        logger.info(f"Job processing interval set to {self.interval_minutes} minutes")
    
    def set_email_limit(self, limit: int):
        """Set the email limit for each processing run"""
        self.email_limit = max(1, limit)  # Minimum 1 email
        logger.info(f"Email limit set to {self.email_limit}")
    
    def process_jobs(self):
        """Process jobs - this is the scheduled function"""
        try:
            logger.info(f"Starting scheduled job processing at {datetime.now()}")
            
            result = job_processor.run_full_workflow(email_limit=self.email_limit)
            
            if result['success']:
                logger.info(f"Scheduled processing completed: {result['jobs_processed']} jobs processed")
            else:
                logger.error(f"Scheduled processing failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in scheduled job processing: {e}")
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Schedule the job processing
            schedule.every(self.interval_minutes).minutes.do(self.process_jobs)
            
            # Run initial processing
            logger.info("Running initial job processing")
            self.process_jobs()
            
            self.running = True
            
            # Start scheduler in a separate thread
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            logger.info(f"Scheduler started with {self.interval_minutes} minute interval")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            self.running = False
    
    def stop(self):
        """Stop the scheduler"""
        if not self.running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.running = False
            schedule.clear()
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            logger.info("Scheduler stopped")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Wait before retrying
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        return {
            'running': self.running,
            'interval_minutes': self.interval_minutes,
            'email_limit': self.email_limit,
            'next_run': schedule.next_run().isoformat() if schedule.jobs else None,
            'last_run': getattr(self, '_last_run', None)
        }
    
    def run_once(self):
        """Run job processing once immediately"""
        try:
            logger.info("Running one-time job processing")
            result = job_processor.run_full_workflow(email_limit=self.email_limit)
            
            if result['success']:
                logger.info(f"One-time processing completed: {result['jobs_processed']} jobs processed")
            else:
                logger.error(f"One-time processing failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in one-time job processing: {e}")
            return {
                'success': False,
                'error': str(e),
                'jobs_processed': 0,
                'jobs_exported': 0,
                'jobs_marked': 0,
                'duration': 0
            }


# Global scheduler instance
job_scheduler = JobScheduler()


def start_scheduler():
    """Start the job scheduler"""
    job_scheduler.start()


def stop_scheduler():
    """Stop the job scheduler"""
    job_scheduler.stop()


if __name__ == "__main__":
    # Example usage
    import signal
    import sys
    
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        stop_scheduler()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start scheduler
    start_scheduler()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        stop_scheduler() 