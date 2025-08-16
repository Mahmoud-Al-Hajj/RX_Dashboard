import logging
import time
from typing import List, Optional
from datetime import datetime

from email_service import email_service
from scraper import job_scraper
from database import db_manager
from excel_exporter import excel_exporter
from models import JobPosting, JobPostingCreate, EmailData, ScrapedJobData
from config import settings

logger = logging.getLogger(__name__)


class JobProcessor:
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
    
    def process_emails(self, limit: int = 10) -> List[JobPosting]:
        """Process emails and extract job postings"""
        try:
            logger.info(f"Starting email processing (limit: {limit})")
            
            # Fetch emails from Gmail
            emails = email_service.fetch_remotelyx_emails(limit=limit)
            
            if not emails:
                logger.info("No emails found to process")
                return []
            
            logger.info(f"Found {len(emails)} emails to process")
            
            processed_jobs = []
            
            for email_data in emails:
                try:
                    job_posting = self._process_single_email(email_data)
                    if job_posting:
                        processed_jobs.append(job_posting)
                        self.processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing email: {e}")
                    self.error_count += 1
                    continue
            
            logger.info(f"Successfully processed {len(processed_jobs)} job postings")
            return processed_jobs
            
        except Exception as e:
            logger.error(f"Error in email processing: {e}")
            return []
    
    def _process_single_email(self, email_data: EmailData) -> Optional[JobPosting]:
        """Process a single email and extract job posting"""
        try:
            # Check if we have a job URL
            if not email_data.job_url:
                logger.warning(f"No job URL found in email: {email_data.subject}")
                return None
            
            # Check if job already exists in database
            existing_job = db_manager.get_job_by_url(email_data.job_url)
            if existing_job:
                logger.info(f"Job already exists: {email_data.job_url}")
                return existing_job
            
            # Scrape job details from the URL
            scraped_data = job_scraper.scrape_job_page(email_data.job_url)
            if not scraped_data:
                logger.error(f"Failed to scrape job page: {email_data.job_url}")
                return None
            
            # Create job posting object
            job_posting = JobPostingCreate(
                job_title=scraped_data.job_title,
                company=scraped_data.company,
                location=scraped_data.location,
                skills=scraped_data.skills,
                salary=scraped_data.salary,
                job_url=email_data.job_url,
                email_subject=email_data.subject,
                email_date=email_data.date
            )
            
            # Save to database
            job_id = db_manager.insert_job_posting(job_posting)
            if not job_id:
                logger.error(f"Failed to save job to database: {email_data.job_url}")
                return None
            
            # Get the complete job posting from database
            saved_job = db_manager.get_job_by_url(email_data.job_url)
            if saved_job:
                logger.info(f"Successfully processed job: {scraped_data.job_title} at {scraped_data.company}")
                return saved_job
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing single email: {e}")
            return None
    
    def export_to_excel(self, jobs: List[JobPosting]) -> bool:
        """Export job postings to Excel file"""
        try:
            if not jobs:
                logger.info("No jobs to export to Excel")
                return True
            
            success = excel_exporter.append_jobs(jobs)
            if success:
                logger.info(f"Successfully exported {len(jobs)} jobs to Excel")
            else:
                logger.error("Failed to export jobs to Excel")
            
            return success
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return False
    
    def mark_jobs_processed(self, jobs: List[JobPosting]) -> int:
        """Mark jobs as processed in database"""
        try:
            marked_count = 0
            for job in jobs:
                if db_manager.mark_job_processed(str(job.id)):
                    marked_count += 1
            
            logger.info(f"Marked {marked_count} jobs as processed")
            return marked_count
            
        except Exception as e:
            logger.error(f"Error marking jobs as processed: {e}")
            return 0
    
    def run_full_workflow(self, email_limit: int = 10) -> dict:
        """Run the complete workflow from email processing to Excel export"""
        start_time = time.time()
        
        try:
            logger.info("Starting full workflow")
            
            # Step 1: Process emails and extract job postings
            jobs = self.process_emails(limit=email_limit)
            
            if not jobs:
                logger.info("No new jobs found in workflow")
                return {
                    'success': True,
                    'jobs_processed': 0,
                    'jobs_exported': 0,
                    'jobs_marked': 0,
                    'duration': time.time() - start_time
                }
            
            # Step 2: Export to Excel
            excel_success = self.export_to_excel(jobs)
            
            # Step 3: Mark jobs as processed
            marked_count = self.mark_jobs_processed(jobs)
            
            duration = time.time() - start_time
            
            result = {
                'success': excel_success,
                'jobs_processed': len(jobs),
                'jobs_exported': len(jobs) if excel_success else 0,
                'jobs_marked': marked_count,
                'duration': duration,
                'errors': self.error_count
            }
            
            logger.info(f"Workflow completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in full workflow: {e}")
            return {
                'success': False,
                'jobs_processed': 0,
                'jobs_exported': 0,
                'jobs_marked': 0,
                'duration': time.time() - start_time,
                'error': str(e)
            }
    
    def get_statistics(self) -> dict:
        """Get processing statistics"""
        try:
            # Get database statistics
            unprocessed_jobs = db_manager.get_unprocessed_jobs()
            all_jobs = db_manager.get_all_jobs(limit=1000)
            
            # Get Excel statistics
            excel_stats = excel_exporter.get_statistics()
            
            stats = {
                'total_jobs_in_db': len(all_jobs),
                'unprocessed_jobs': len(unprocessed_jobs),
                'processed_count': self.processed_count,
                'error_count': self.error_count,
                'excel_stats': excel_stats,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                'error': str(e),
                'last_updated': datetime.utcnow().isoformat()
            }
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            email_service.disconnect()
            job_scraper.close()
            db_manager.close()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global job processor instance
job_processor = JobProcessor() 