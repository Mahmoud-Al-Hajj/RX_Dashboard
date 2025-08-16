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