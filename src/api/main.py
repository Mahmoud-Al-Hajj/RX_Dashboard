"""
FastAPI application for RemotelyX Job Automation Service.
Provides REST API endpoints for job management and automation workflows.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from ..core.config import get_settings
from ..core.database import get_database
from ..models.job_posting import (
    JobPosting, JobPostingCreate, JobPostingUpdate, 
    ScrapingResult, DashboardFilters
)
from ..services.job_processor import job_processor


# Create FastAPI app
app = FastAPI(
    title="RemotelyX Job Automation API",
    description="API for automated job posting scraping, processing, and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get database
async def get_db():
    return await get_database()


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        settings = get_settings()
        settings.ensure_directories()
        
        # Initialize job processor
        success = await job_processor.initialize()
        if not success:
            logger.error("Failed to initialize job processor")
        
        logger.success("RemotelyX Job Automation API started successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        await job_processor.cleanup()
        logger.info("RemotelyX Job Automation API shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        db = await get_db()
        db_connected = db.is_connected()
        
        return {
            "status": "healthy" if db_connected else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected" if db_connected else "disconnected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "RemotelyX Job Automation API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# Job management endpoints
@app.get("/jobs", response_model=List[JobPosting])
async def get_jobs(
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    processed: Optional[bool] = None,
    enriched: Optional[bool] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    db = Depends(get_db)
):
    """Get job postings with optional filters."""
    try:
        jobs = await db.get_jobs(
            limit=limit,
            skip=skip,
            processed=processed,
            enriched=enriched,
            company=company,
            location=location
        )
        return jobs
    except Exception as e:
        logger.error(f"Failed to get jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs")


@app.get("/jobs/{job_id}", response_model=JobPosting)
async def get_job(job_id: str, db = Depends(get_db)):
    """Get a specific job posting by ID."""
    try:
        job = await db.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job")


@app.post("/jobs", response_model=JobPosting)
async def create_job(job_data: JobPostingCreate, db = Depends(get_db)):
    """Create a new job posting."""
    try:
        job_id = await db.insert_job(job_data)
        if not job_id:
            raise HTTPException(status_code=400, detail="Failed to create job")
        
        job = await db.get_job(job_id)
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail="Failed to create job")


@app.put("/jobs/{job_id}", response_model=JobPosting)
async def update_job(job_id: str, update_data: JobPostingUpdate, db = Depends(get_db)):
    """Update a job posting."""
    try:
        success = await db.update_job(job_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = await db.get_job(job_id)
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update job")


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str, db = Depends(get_db)):
    """Delete a job posting."""
    try:
        success = await db.delete_job(job_id)
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {"message": "Job deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete job")


# Workflow endpoints
@app.post("/workflow/run")
async def run_workflow(
    job_urls: List[str],
    background_tasks: BackgroundTasks
):
    """Run the complete job processing workflow."""
    try:
        if not job_urls:
            raise HTTPException(status_code=400, detail="No job URLs provided")
        
        # Run workflow in background
        background_tasks.add_task(job_processor.run_full_workflow, job_urls)
        
        return {
            "message": "Workflow started",
            "job_count": len(job_urls),
            "status": "processing"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to start workflow")


@app.post("/workflow/scrape")
async def scrape_jobs(job_urls: List[str]):
    """Scrape job postings from URLs."""
    try:
        if not job_urls:
            raise HTTPException(status_code=400, detail="No job URLs provided")
        
        result = await job_processor.process_jobs(job_urls)
        return result.dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to scrape jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to scrape jobs")


@app.post("/workflow/enrich")
async def enrich_jobs(limit: int = Query(100, ge=1, le=1000)):
    """Enrich job postings with additional data."""
    try:
        result = await job_processor.enrich_jobs(limit=limit)
        return result
    except Exception as e:
        logger.error(f"Failed to enrich jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to enrich jobs")


# Statistics endpoints
@app.get("/statistics")
async def get_statistics():
    """Get comprehensive statistics."""
    try:
        stats = await job_processor.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@app.get("/companies")
async def get_companies(db = Depends(get_db)):
    """Get list of all companies."""
    try:
        companies = await db.get_companies()
        return {"companies": companies}
    except Exception as e:
        logger.error(f"Failed to get companies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get companies")


@app.get("/locations")
async def get_locations(db = Depends(get_db)):
    """Get list of all locations."""
    try:
        locations = await db.get_locations()
        return {"locations": locations}
    except Exception as e:
        logger.error(f"Failed to get locations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get locations")


@app.get("/skills")
async def get_skills(db = Depends(get_db)):
    """Get list of all skills."""
    try:
        skills = await db.get_skills()
        return {"skills": skills}
    except Exception as e:
        logger.error(f"Failed to get skills: {e}")
        raise HTTPException(status_code=500, detail="Failed to get skills")


# Excel export endpoints
@app.post("/excel/export")
async def export_to_excel():
    """Export all jobs to Excel."""
    try:
        result = await job_processor.export_to_excel()
        return result
    except Exception as e:
        logger.error(f"Failed to export to Excel: {e}")
        raise HTTPException(status_code=500, detail="Failed to export to Excel")


@app.post("/excel/backup")
async def create_backup():
    """Create a backup of the Excel file."""
    try:
        from ..services.excel_exporter import excel_exporter
        result = excel_exporter.create_backup()
        return result
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(status_code=500, detail="Failed to create backup")


@app.get("/excel/backups")
async def list_backups():
    """List all available backups."""
    try:
        from ..services.excel_exporter import excel_exporter
        backups = excel_exporter.list_backups()
        return {"backups": backups}
    except Exception as e:
        logger.error(f"Failed to list backups: {e}")
        raise HTTPException(status_code=500, detail="Failed to list backups")


@app.post("/excel/restore/{backup_filename}")
async def restore_backup(backup_filename: str):
    """Restore from a backup file."""
    try:
        from ..services.excel_exporter import excel_exporter
        result = excel_exporter.restore_backup(backup_filename)
        return result
    except Exception as e:
        logger.error(f"Failed to restore backup: {e}")
        raise HTTPException(status_code=500, detail="Failed to restore backup")


# Dashboard endpoints
@app.post("/dashboard/filter")
async def filter_jobs(filters: DashboardFilters, db = Depends(get_db)):
    """Filter jobs based on criteria."""
    try:
        # This would implement advanced filtering logic
        # For now, return basic filtered results
        jobs = await db.get_jobs(limit=1000)
        
        # Apply filters (simplified implementation)
        filtered_jobs = []
        for job in jobs:
            if filters.companies and job.company not in filters.companies:
                continue
            if filters.locations and job.location not in filters.locations:
                continue
            if filters.seniority_levels and job.seniority_level not in filters.seniority_levels:
                continue
            if filters.work_modes and job.work_mode not in filters.work_modes:
                continue
            if filters.employment_types and job.employment_type not in filters.employment_types:
                continue
            
            filtered_jobs.append(job)
        
        return {
            "jobs": filtered_jobs,
            "total": len(filtered_jobs),
            "filters_applied": filters.dict()
        }
    except Exception as e:
        logger.error(f"Failed to filter jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to filter jobs")


@app.get("/dashboard/quick-check")
async def get_quick_check_metrics(db = Depends(get_db)):
    """Get quick check metrics for the dashboard."""
    try:
        # Get basic statistics
        stats = await db.get_statistics()
        
        # Calculate additional metrics
        total_jobs = stats.total_jobs
        top_skills_count = len(stats.top_skills)
        top_roles_count = len(stats.by_seniority)
        total_applications = total_jobs  # In real implementation, this would be separate
        
        return {
            "total_jobs": total_jobs,
            "top_skills": top_skills_count,
            "top_roles": top_roles_count,
            "total_applications": total_applications,
            "processed_jobs": stats.processed_jobs,
            "enriched_jobs": stats.enriched_jobs,
            "companies_count": len(stats.by_company)
        }
    except Exception as e:
        logger.error(f"Failed to get quick check metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quick check metrics")


@app.get("/dashboard/pipeline")
async def get_pipeline_data(db = Depends(get_db)):
    """Get pipeline and hiring data."""
    try:
        # Get all jobs for analysis
        jobs = await db.get_jobs(limit=1000)
        
        # Application funnel data (sample data - in real implementation this would come from actual application tracking)
        application_funnel = {
            "categories": ["UX/UI", "Web Dev", "Marketing", "Finance", "Others"],
            "stages": ["Applied", "Interviewed", "Rejected", "Hired"],
            "data": {
                "UX/UI": [45, 25, 15, 8],
                "Web Dev": [60, 35, 20, 12],
                "Marketing": [30, 18, 10, 5],
                "Finance": [25, 15, 8, 4],
                "Others": [40, 22, 12, 6]
            }
        }
        
        # Salary range analysis
        salary_ranges = ["$800-1k", "$1k-1.5k", "$1.5k-2k", "$2-2.5k", "$2.5k-3k", "$3k-3.5k", "$3.5k+"]
        salary_data = [120, 180, 220, 160, 140, 90, 60]
        
        # Companies hiring analysis
        companies_hiring = []
        for company, count in list(stats.by_company.items())[:10]:  # Top 10 companies
            companies_hiring.append({
                "company": company,
                "job_count": count,
                "active": True  # In real implementation, this would check recent activity
            })
        
        return {
            "application_funnel": application_funnel,
            "salary_ranges": {
                "ranges": salary_ranges,
                "counts": salary_data
            },
            "companies_hiring": companies_hiring,
            "total_companies": len(stats.by_company)
        }
    except Exception as e:
        logger.error(f"Failed to get pipeline data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pipeline data")


@app.get("/dashboard/trends")
async def get_trends_data(db = Depends(get_db)):
    """Get trends and activity data."""
    try:
        # Get all jobs for analysis
        jobs = await db.get_jobs(limit=1000)
        
        # Job activity over time (last 7 days)
        dates = []
        job_postings = []
        previous_period = []
        
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            dates.append(date.strftime('%Y-%m-%d'))
            
            # Count jobs posted on this date (simplified)
            day_jobs = len([j for j in jobs if j.posting_date and j.posting_date.date() == date.date()])
            job_postings.append(day_jobs)
            
            # Previous period (simplified)
            previous_period.append(max(0, day_jobs - 2))
        
        # Location distribution
        location_distribution = []
        for location, count in list(stats.by_location.items())[:5]:  # Top 5 locations
            location_distribution.append({
                "location": location,
                "count": count,
                "percentage": round((count / stats.total_jobs) * 100, 1) if stats.total_jobs > 0 else 0
            })
        
        # Seniority distribution
        seniority_distribution = []
        for seniority, count in stats.by_seniority.items():
            seniority_distribution.append({
                "seniority": seniority,
                "count": count,
                "percentage": round((count / stats.total_jobs) * 100, 1) if stats.total_jobs > 0 else 0
            })
        
        # Skills trends
        skills_trends = []
        for skill_data in stats.top_skills[:10]:  # Top 10 skills
            skills_trends.append({
                "skill": skill_data["skill"],
                "count": skill_data["count"],
                "trend": "up" if skill_data["count"] > 10 else "stable"  # Simplified trend
            })
        
        return {
            "activity_timeline": {
                "dates": dates,
                "job_postings": job_postings,
                "previous_period": previous_period
            },
            "location_distribution": location_distribution,
            "seniority_distribution": seniority_distribution,
            "skills_trends": skills_trends,
            "total_jobs_analyzed": len(jobs)
        }
    except Exception as e:
        logger.error(f"Failed to get trends data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get trends data")


@app.get("/dashboard/analytics")
async def get_dashboard_analytics(db = Depends(get_db)):
    """Get comprehensive dashboard analytics."""
    try:
        # Get all data in one call
        quick_check = await get_quick_check_metrics(db)
        pipeline = await get_pipeline_data(db)
        trends = await get_trends_data(db)
        
        return {
            "quick_check": quick_check,
            "pipeline": pipeline,
            "trends": trends,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard analytics")


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 