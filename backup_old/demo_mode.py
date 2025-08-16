#!/usr/bin/env python3
"""
Demo Mode for RemotelyX Job Automation Service
This allows testing the UI without real credentials or database.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Mock data for demo
MOCK_JOBS = [
    {
        "id": "demo_1",
        "job_title": "Senior Python Developer",
        "company": "TechCorp Inc",
        "location": "Remote",
        "skills": ["Python", "Django", "React", "AWS"],
        "salary": "$80,000 - $120,000",
        "job_url": "https://example.com/job/1",
        "email_subject": "New Remote Python Position",
        "email_date": datetime.now() - timedelta(hours=2),
        "scraped_at": datetime.now() - timedelta(hours=1),
        "processed": True
    },
    {
        "id": "demo_2", 
        "job_title": "Full Stack Developer",
        "company": "StartupXYZ",
        "location": "San Francisco, CA",
        "skills": ["JavaScript", "Node.js", "MongoDB", "React"],
        "salary": "$90,000 - $130,000",
        "job_url": "https://example.com/job/2",
        "email_subject": "Exciting Full Stack Opportunity",
        "email_date": datetime.now() - timedelta(hours=4),
        "scraped_at": datetime.now() - timedelta(hours=3),
        "processed": False
    },
    {
        "id": "demo_3",
        "job_title": "DevOps Engineer",
        "company": "CloudTech Solutions",
        "location": "Remote",
        "skills": ["Docker", "Kubernetes", "AWS", "Terraform"],
        "salary": "$100,000 - $140,000",
        "job_url": "https://example.com/job/3",
        "email_subject": "DevOps Role Available",
        "email_date": datetime.now() - timedelta(hours=6),
        "scraped_at": datetime.now() - timedelta(hours=5),
        "processed": True
    }
]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RemotelyX Job Automation - DEMO MODE",
    description="Demo version for testing UI without real credentials",
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
    email_limit: int = 5

class WorkflowResponse(BaseModel):
    success: bool
    jobs_processed: int
    jobs_exported: int
    jobs_marked: int
    duration: float
    errors: int
    message: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RemotelyX Job Automation API - DEMO MODE",
        "version": "1.0.0",
        "status": "running",
        "mode": "demo"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "demo_mode",
        "mode": "demo",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/workflow/run", response_model=WorkflowResponse)
async def run_workflow(request: WorkflowRequest):
    """Run the complete job processing workflow - DEMO"""
    logger.info(f"Demo workflow triggered with email limit: {request.email_limit}")
    
    # Simulate processing time
    import time
    time.sleep(1)
    
    return WorkflowResponse(
        success=True,
        jobs_processed=len(MOCK_JOBS),
        jobs_exported=len(MOCK_JOBS),
        jobs_marked=len([j for j in MOCK_JOBS if not j["processed"]]),
        duration=1.2,
        errors=0,
        message="Demo workflow completed successfully"
    )

@app.get("/jobs")
async def get_jobs(limit: int = 100, processed: bool = None):
    """Get job postings from database - DEMO"""
    jobs = MOCK_JOBS.copy()
    
    if processed is not None:
        jobs = [j for j in jobs if j["processed"] == processed]
    
    return jobs[:limit]

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get a specific job posting by ID - DEMO"""
    for job in MOCK_JOBS:
        if job["id"] == job_id:
            return job
    
    raise HTTPException(status_code=404, detail="Job not found")

@app.get("/statistics")
async def get_statistics():
    """Get processing statistics - DEMO"""
    return {
        "total_jobs_in_db": len(MOCK_JOBS),
        "unprocessed_jobs": len([j for j in MOCK_JOBS if not j["processed"]]),
        "processed_count": len([j for j in MOCK_JOBS if j["processed"]]),
        "error_count": 0,
        "excel_stats": {
            "total_jobs": len(MOCK_JOBS),
            "companies": list(set(j["company"] for j in MOCK_JOBS)),
            "locations": list(set(j["location"] for j in MOCK_JOBS)),
            "last_updated": datetime.now().isoformat()
        },
        "last_updated": datetime.now().isoformat(),
        "mode": "demo"
    }

@app.post("/excel/export")
async def export_to_excel():
    """Export all unprocessed jobs to Excel - DEMO"""
    unprocessed_jobs = [j for j in MOCK_JOBS if not j["processed"]]
    
    return {
        "message": "Demo export completed successfully",
        "exported": len(unprocessed_jobs),
        "marked_processed": len(unprocessed_jobs),
        "mode": "demo"
    }

@app.post("/excel/backup")
async def backup_excel():
    """Create a backup of the Excel file - DEMO"""
    return {
        "message": "Demo backup created successfully",
        "mode": "demo"
    }

@app.get("/excel/statistics")
async def get_excel_statistics():
    """Get Excel file statistics - DEMO"""
    return {
        "total_jobs": len(MOCK_JOBS),
        "companies": list(set(j["company"] for j in MOCK_JOBS)),
        "locations": list(set(j["location"] for j in MOCK_JOBS)),
        "last_updated": datetime.now().isoformat(),
        "mode": "demo"
    }

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job posting - DEMO"""
    for job in MOCK_JOBS:
        if job["id"] == job_id:
            return {"message": "Demo job deleted successfully", "mode": "demo"}
    
    raise HTTPException(status_code=404, detail="Job not found")

def main():
    """Run the demo server"""
    print("🚀 Starting RemotelyX Job Automation - DEMO MODE")
    print("=" * 50)
    print("This is a demo version that doesn't require:")
    print("- Gmail credentials")
    print("- MongoDB database")
    print("- Real job postings")
    print()
    print("API will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main() 