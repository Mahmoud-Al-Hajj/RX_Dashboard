from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from typing import List, Optional
from models import JobPosting, JobPostingCreate
from config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client[settings.mongodb_database]
            self.collection = self.db[settings.mongodb_collection]
            
            # Create indexes for better performance
            self.collection.create_index("job_url", unique=True)
            self.collection.create_index("email_date")
            self.collection.create_index("processed")
            
            logger.info("Successfully connected to MongoDB")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def insert_job_posting(self, job_posting: JobPostingCreate) -> Optional[str]:
        """Insert a new job posting"""
        try:
            # Check if job already exists
            existing = self.collection.find_one({"job_url": job_posting.job_url})
            if existing:
                logger.info(f"Job posting already exists: {job_posting.job_url}")
                return str(existing["_id"])
            
            # Insert new job posting
            result = self.collection.insert_one(job_posting.dict())
            logger.info(f"Inserted new job posting: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error inserting job posting: {e}")
            return None
    
    def get_unprocessed_jobs(self) -> List[JobPosting]:
        """Get all unprocessed job postings"""
        try:
            cursor = self.collection.find({"processed": False})
            return [JobPosting(**doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Error fetching unprocessed jobs: {e}")
            return []
    
    def mark_job_processed(self, job_id: str) -> bool:
        """Mark a job posting as processed"""
        try:
            from bson import ObjectId
            result = self.collection.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": {"processed": True}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error marking job as processed: {e}")
            return False
    
    def get_job_by_url(self, job_url: str) -> Optional[JobPosting]:
        """Get job posting by URL"""
        try:
            doc = self.collection.find_one({"job_url": job_url})
            return JobPosting(**doc) if doc else None
        except Exception as e:
            logger.error(f"Error fetching job by URL: {e}")
            return None
    
    def get_all_jobs(self, limit: int = 100) -> List[JobPosting]:
        """Get all job postings with limit"""
        try:
            cursor = self.collection.find().sort("email_date", -1).limit(limit)
            return [JobPosting(**doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Error fetching all jobs: {e}")
            return []


# Global database instance
db_manager = DatabaseManager() 