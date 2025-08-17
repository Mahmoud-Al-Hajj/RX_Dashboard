"""
Data models for RemotelyX job postings and related entities.
Defines the structure and validation for job data according to hackathon requirements.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class SeniorityLevel(str, Enum):
    """Seniority levels for job positions."""
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    EXECUTIVE = "Executive"


class WorkMode(str, Enum):
    """Work mode classifications."""
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ONSITE = "Onsite"


class EmploymentType(str, Enum):
    """Employment type classifications."""
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    FREELANCE = "Freelance"


class PyObjectId(ObjectId):
    """Custom ObjectId for MongoDB integration."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string")
        return field_schema


class JobPostingBase(BaseModel):
    """Base model for job posting data with simplified fields."""
    
    # Core Information
    title: str = Field(..., description="Job title")
    job_url: str = Field(..., description="URL to the job posting")
    description: str = Field(..., description="Job description")
    
    # Skills & Requirements
    skills: List[str] = Field(default_factory=list, description="Required skills/technologies")
    
    # Job Details
    seniority: Optional[str] = Field(None, description="Seniority level")
    work_mode: Optional[str] = Field(None, description="Work mode")
    
    # Compensation
    salary_min: Optional[float] = Field(None, description="Minimum salary")
    salary_max: Optional[float] = Field(None, description="Maximum salary")
    
    @validator('skills')
    def validate_skills(cls, v):
        """Validate and clean skills list."""
        if v is None:
            return []
        return [item.strip() for item in v if item.strip()]
    
    @validator('title', 'job_url', 'description')
    def validate_required_fields(cls, v):
        """Validate required fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    @validator('salary_min', 'salary_max')
    def validate_salary(cls, v):
        """Validate salary values."""
        if v is not None and v < 0:
            raise ValueError("Salary cannot be negative")
        return v


class JobPostingCreate(JobPostingBase):
    """Model for creating a new job posting."""
    pass


class JobPosting(JobPostingBase):
    """Complete job posting model with database fields."""
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    processed: bool = Field(default=False, description="Processing status")
    enriched: bool = Field(default=False, description="Enrichment status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Enrichment fields
    extracted_skills: List[str] = Field(default_factory=list, description="Extracted technical skills")
    inferred_seniority: Optional[SeniorityLevel] = Field(None, description="Inferred seniority level")
    inferred_work_mode: Optional[WorkMode] = Field(None, description="Inferred work mode")
    salary_range_parsed: Optional[Dict[str, Any]] = Field(None, description="Parsed salary information")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class JobPostingUpdate(BaseModel):
    """Model for updating job posting fields."""
    
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    seniority_level: Optional[SeniorityLevel] = None
    work_mode: Optional[WorkMode] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    skills: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    processed: Optional[bool] = None
    enriched: Optional[bool] = None
    
    class Config:
        populate_by_name = True


class JobStatistics(BaseModel):
    """Model for job statistics and analytics."""
    
    total_jobs: int = Field(0, description="Total number of jobs")
    processed_jobs: int = Field(0, description="Number of processed jobs")
    enriched_jobs: int = Field(0, description="Number of enriched jobs")
    
    # Breakdowns
    by_seniority: Dict[str, int] = Field(default_factory=dict, description="Jobs by seniority")
    by_work_mode: Dict[str, int] = Field(default_factory=dict, description="Jobs by work mode")
    by_employment_type: Dict[str, int] = Field(default_factory=dict, description="Jobs by employment type")
    by_company: Dict[str, int] = Field(default_factory=dict, description="Jobs by company")
    by_location: Dict[str, int] = Field(default_factory=dict, description="Jobs by location")
    
    # Skills analysis
    top_skills: List[Dict[str, Any]] = Field(default_factory=list, description="Top skills frequency")
    skills_frequency: Dict[str, int] = Field(default_factory=dict, description="Skills frequency")
    
    # Salary analysis
    salary_stats: Dict[str, Any] = Field(default_factory=dict, description="Salary statistics")
    
    # Timeline
    posting_timeline: Dict[str, int] = Field(default_factory=dict, description="Jobs by posting date")
    
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update time")


class ScrapingResult(BaseModel):
    """Model for scraping operation results."""
    
    success: bool = Field(..., description="Scraping success status")
    jobs_found: int = Field(0, description="Number of jobs found")
    jobs_processed: int = Field(0, description="Number of jobs processed")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    duration: float = Field(0.0, description="Scraping duration in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Scraping timestamp")


class DashboardFilters(BaseModel):
    """Model for dashboard filtering options."""
    
    companies: List[str] = Field(default_factory=list, description="Filter by companies")
    locations: List[str] = Field(default_factory=list, description="Filter by locations")
    seniority_levels: List[SeniorityLevel] = Field(default_factory=list, description="Filter by seniority")
    work_modes: List[WorkMode] = Field(default_factory=list, description="Filter by work mode")
    employment_types: List[EmploymentType] = Field(default_factory=list, description="Filter by employment type")
    skills: List[str] = Field(default_factory=list, description="Filter by skills")
    salary_min: Optional[float] = Field(None, description="Minimum salary filter")
    salary_max: Optional[float] = Field(None, description="Maximum salary filter")
    date_from: Optional[datetime] = Field(None, description="Start date filter")
    date_to: Optional[datetime] = Field(None, description="End date filter") 