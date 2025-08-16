from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
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


class JobPosting(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    job_title: str
    company: str
    location: str
    skills: List[str] = []
    salary: Optional[str] = None
    job_url: str
    email_subject: str
    email_date: datetime
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class JobPostingCreate(BaseModel):
    job_title: str
    company: str
    location: str
    skills: List[str] = []
    salary: Optional[str] = None
    job_url: str
    email_subject: str
    email_date: datetime


class EmailData(BaseModel):
    subject: str
    sender: str
    date: datetime
    body: str
    job_url: Optional[str] = None


class ScrapedJobData(BaseModel):
    job_title: str
    company: str
    location: str
    skills: List[str]
    salary: Optional[str] = None 