"""
Main job processor for RemotelyX job automation.
Orchestrates scraping, processing, enrichment, and storage operations.
"""

import asyncio
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from ..core.config import get_settings
from ..core.database import get_database
from ..models.job_posting import JobPostingCreate, JobPostingUpdate, ScrapingResult
from ..services.scraper import scraper
from ..services.excel_exporter import excel_exporter


class JobProcessor:
    """Main processor for job automation workflow."""
    
    def __init__(self):
        self.settings = get_settings()
        self.db = None
    
    async def initialize(self) -> bool:
        """Initialize the job processor."""
        try:
            self.db = await get_database()
            connected = await self.db.connect()
            if not connected:
                logger.error("Failed to connect to database")
                return False
            
            logger.success("Job processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize job processor: {e}")
            return False
    
    async def process_jobs(self, job_urls: List[str]) -> ScrapingResult:
        """Process a list of job URLs."""
        start_time = time.time()
        jobs_found = len(job_urls)
        jobs_processed = 0
        errors = []
        
        logger.info(f"Starting to process {jobs_found} job URLs")
        
        for i, url in enumerate(job_urls, 1):
            try:
                logger.info(f"Processing job {i}/{jobs_found}: {url}")
                
                # Scrape job posting
                job_data = scraper.scrape_job_posting(url)
                if not job_data:
                    errors.append(f"Failed to scrape job: {url}")
                    continue
                
                # Store in database
                job_id = await self.db.insert_job(job_data)
                if job_id:
                    jobs_processed += 1
                    logger.success(f"Successfully processed job: {job_data.title}")
                else:
                    errors.append(f"Failed to store job: {url}")
                
            except Exception as e:
                error_msg = f"Error processing job {url}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        duration = time.time() - start_time
        
        result = ScrapingResult(
            success=jobs_processed > 0,
            jobs_found=jobs_found,
            jobs_processed=jobs_processed,
            errors=errors,
            duration=duration,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Job processing completed: {jobs_processed}/{jobs_found} jobs processed in {duration:.2f}s")
        return result
    
    async def enrich_jobs(self, limit: int = 100) -> Dict[str, Any]:
        """Enrich unenriched job postings with additional data."""
        try:
            logger.info(f"Starting job enrichment (limit: {limit})")
            
            # Get unenriched jobs
            jobs = await self.db.get_jobs(limit=limit, enriched=False)
            if not jobs:
                logger.info("No unenriched jobs found")
                return {"enriched": 0, "total": 0}
            
            enriched_count = 0
            
            for job in jobs:
                try:
                    # Perform enrichment
                    enriched_data = await self._enrich_job(job)
                    if enriched_data:
                        # Update job in database
                        update_data = JobPostingUpdate(
                            extracted_skills=enriched_data.get("extracted_skills", []),
                            inferred_seniority=enriched_data.get("inferred_seniority"),
                            inferred_work_mode=enriched_data.get("inferred_work_mode"),
                            salary_range_parsed=enriched_data.get("salary_range_parsed"),
                            enriched=True
                        )
                        
                        success = await self.db.update_job(str(job.id), update_data)
                        if success:
                            enriched_count += 1
                            logger.debug(f"Enriched job: {job.title}")
                
                except Exception as e:
                    logger.error(f"Failed to enrich job {job.title}: {e}")
            
            logger.success(f"Job enrichment completed: {enriched_count}/{len(jobs)} jobs enriched")
            return {
                "enriched": enriched_count,
                "total": len(jobs)
            }
            
        except Exception as e:
            logger.error(f"Job enrichment failed: {e}")
            return {"enriched": 0, "total": 0, "error": str(e)}
    
    async def _enrich_job(self, job) -> Optional[Dict[str, Any]]:
        """Enrich a single job with additional data."""
        try:
            enriched_data = {}
            
            # Extract additional skills from description
            if job.description:
                enriched_data["extracted_skills"] = self._extract_additional_skills(job.description)
            
            # Infer seniority if not already set
            if not job.seniority_level and job.title:
                enriched_data["inferred_seniority"] = self._infer_seniority_from_text(job.title, job.description)
            
            # Infer work mode if not already set
            if not job.work_mode:
                enriched_data["inferred_work_mode"] = self._infer_work_mode_from_text(job.title, job.description)
            
            # Parse salary range if available
            if job.salary_min or job.salary_max:
                enriched_data["salary_range_parsed"] = {
                    "min": job.salary_min,
                    "max": job.salary_max,
                    "currency": job.salary_currency,
                    "period": job.salary_period
                }
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Failed to enrich job: {e}")
            return None
    
    def _extract_additional_skills(self, text: str) -> List[str]:
        """Extract additional skills from text."""
        # This could be enhanced with NLP or ML models
        # For now, using basic keyword matching
        additional_skills = []
        
        # Add more sophisticated skill extraction logic here
        # Could use NLTK, spaCy, or other NLP libraries
        
        return additional_skills
    
    def _infer_seniority_from_text(self, title: str, description: str) -> Optional[str]:
        """Infer seniority level from text."""
        text = f"{title} {description}".lower()
        
        seniority_keywords = {
            "Junior": ["junior", "entry", "entry-level", "jr", "graduate", "new grad"],
            "Mid": ["mid", "middle", "intermediate", "mid-level"],
            "Senior": ["senior", "sr", "senior-level", "experienced"],
            "Lead": ["lead", "team lead", "technical lead"],
            "Executive": ["executive", "director", "vp", "cto", "ceo"]
        }
        
        for level, keywords in seniority_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return level
        
        return None
    
    def _infer_work_mode_from_text(self, title: str, description: str) -> Optional[str]:
        """Infer work mode from text."""
        text = f"{title} {description}".lower()
        
        work_mode_keywords = {
            "Remote": ["remote", "work from home", "wfh", "fully remote"],
            "Hybrid": ["hybrid", "partially remote", "flexible"],
            "Onsite": ["onsite", "on-site", "in-office", "office-based"]
        }
        
        for mode, keywords in work_mode_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return mode
        
        return None
    
    async def export_to_excel(self) -> Dict[str, Any]:
        """Export all jobs to Excel."""
        try:
            logger.info("Starting Excel export")
            
            # Get all jobs
            jobs = await self.db.get_jobs(limit=10000)  # Large limit to get all jobs
            
            if not jobs:
                logger.warning("No jobs to export")
                return {"success": False, "error": "No jobs to export"}
            
            # Export to Excel
            result = excel_exporter.export_jobs_to_excel(jobs)
            
            if result["success"]:
                logger.success(f"Excel export completed: {result['exported']} jobs exported")
            else:
                logger.error(f"Excel export failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_full_workflow(self, job_urls: List[str]) -> Dict[str, Any]:
        """Run the complete workflow: scrape → store → enrich → export."""
        try:
            logger.info("Starting full workflow")
            start_time = time.time()
            
            # Step 1: Process jobs
            scraping_result = await self.process_jobs(job_urls)
            
            # Step 2: Enrich jobs
            enrichment_result = await self.enrich_jobs()
            
            # Step 3: Export to Excel
            export_result = await self.export_to_excel()
            
            duration = time.time() - start_time
            
            workflow_result = {
                "success": scraping_result.success and export_result.get("success", False),
                "duration": duration,
                "scraping": scraping_result.dict(),
                "enrichment": enrichment_result,
                "export": export_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.success(f"Full workflow completed in {duration:.2f}s")
            return workflow_result
            
        except Exception as e:
            logger.error(f"Full workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": 0
            }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        try:
            # Get database statistics
            db_stats = await self.db.get_statistics()
            
            # Get Excel statistics
            excel_stats = excel_exporter.get_excel_statistics()
            
            # Combine statistics
            stats = {
                "database": db_stats.dict(),
                "excel": excel_stats,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.db:
            await self.db.disconnect()
        logger.info("Job processor cleanup completed")


# Global job processor instance
job_processor = JobProcessor() 