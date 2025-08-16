from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import uvicorn

from job_processor import job_processor
from database import db_manager
from excel_exporter import excel_exporter
from models import JobPosting
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

# Create FastAPI app
app = FastAPI(
    title="RemotelyX Job Automation API",
    description="Backend service for automating RemotelyX job description processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WorkflowRequest(BaseModel):
    email_limit: Optional[int] = 10


class WorkflowResponse(BaseModel):
    success: bool
    jobs_processed: int
    jobs_exported: int
    jobs_marked: int
    duration: float
    errors: int
    message: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        ensure_directories()
        logger.info("RemotelyX Job Automation API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        job_processor.cleanup()
        logger.info("RemotelyX Job Automation API shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RemotelyX Job Automation API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_manager.client.admin.command('ping')
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/workflow/run", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """Run the complete job processing workflow"""
    try:
        logger.info(f"Starting workflow with email limit: {request.email_limit}")
        
        # Run workflow in background to avoid blocking
        result = job_processor.run_full_workflow(email_limit=request.email_limit)
        
        return WorkflowResponse(
            success=result['success'],
            jobs_processed=result['jobs_processed'],
            jobs_exported=result['jobs_exported'],
            jobs_marked=result['jobs_marked'],
            duration=result['duration'],
            errors=result.get('errors', 0),
            message="Workflow completed successfully" if result['success'] else "Workflow failed"
        )
        
    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")


@app.get("/jobs", response_model=List[JobPosting])
async def get_jobs(limit: int = 100, processed: Optional[bool] = None):
    """Get job postings from database"""
    try:
        if processed is None:
            jobs = db_manager.get_all_jobs(limit=limit)
        elif processed:
            jobs = db_manager.get_all_jobs(limit=limit)  # All jobs
        else:
            jobs = db_manager.get_unprocessed_jobs()
        
        return jobs
        
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {str(e)}")


@app.get("/jobs/{job_id}", response_model=JobPosting)
async def get_job(job_id: str):
    """Get a specific job posting by ID"""
    try:
        from bson import ObjectId
        job = db_manager.collection.find_one({"_id": ObjectId(job_id)})
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobPosting(**job)
        
    except Exception as e:
        logger.error(f"Error fetching job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch job: {str(e)}")


@app.get("/statistics")
async def get_statistics():
    """Get processing statistics"""
    try:
        stats = job_processor.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@app.post("/excel/export")
async def export_to_excel():
    """Export all unprocessed jobs to Excel"""
    try:
        unprocessed_jobs = db_manager.get_unprocessed_jobs()
        
        if not unprocessed_jobs:
            return {"message": "No unprocessed jobs to export", "exported": 0}
        
        success = excel_exporter.append_jobs(unprocessed_jobs)
        
        if success:
            # Mark jobs as processed
            marked_count = job_processor.mark_jobs_processed(unprocessed_jobs)
            
            return {
                "message": "Export completed successfully",
                "exported": len(unprocessed_jobs),
                "marked_processed": marked_count
            }
        else:
            raise HTTPException(status_code=500, detail="Export failed")
            
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.post("/excel/backup")
async def backup_excel():
    """Create a backup of the Excel file"""
    try:
        success = excel_exporter.backup_file()
        
        if success:
            return {"message": "Backup created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Backup failed")
            
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@app.get("/excel/statistics")
async def get_excel_statistics():
    """Get Excel file statistics"""
    try:
        stats = excel_exporter.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting Excel statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Excel statistics: {str(e)}")


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job posting"""
    try:
        from bson import ObjectId
        result = db_manager.collection.delete_one({"_id": ObjectId(job_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {"message": "Job deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete job: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    ) 