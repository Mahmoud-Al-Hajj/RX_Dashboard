"""
Database layer for RemotelyX Job Automation Service.
Handles MongoDB connections and operations with proper error handling.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from loguru import logger

from ..core.config import get_settings
from ..models.job_posting import JobPosting, JobPostingCreate, JobPostingUpdate, JobStatistics


class DatabaseManager:
    """Manages MongoDB database connections and operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.collection: Optional[Collection] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Establish connection to MongoDB."""
        try:
            logger.info(f"Connecting to MongoDB at {self.settings.mongodb_uri}")
            
            self.client = MongoClient(
                self.settings.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            self.database = self.client[self.settings.mongodb_database]
            self.collection = self.database[self.settings.mongodb_collection]
            
            # Create indexes
            await self._create_indexes()
            
            self._connected = True
            logger.success("Successfully connected to MongoDB")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self) -> None:
        """Create necessary database indexes."""
        try:
            # Create indexes for better query performance
            self.collection.create_index([("title", 1)])
            self.collection.create_index([("company", 1)])
            self.collection.create_index([("location", 1)])
            self.collection.create_index([("job_url", 1)], unique=True)
            self.collection.create_index([("posting_date", -1)])
            self.collection.create_index([("created_at", -1)])
            self.collection.create_index([("processed", 1)])
            self.collection.create_index([("enriched", 1)])
            self.collection.create_index([("skills", 1)])
            self.collection.create_index([("seniority_level", 1)])
            self.collection.create_index([("work_mode", 1)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connected and self.client is not None
    
    async def insert_job(self, job_data: JobPostingCreate) -> Optional[str]:
        """Insert a new job posting."""
        if not self.is_connected():
            logger.error("Database not connected")
            return None
        
        try:
            # Check if job already exists
            existing = self.collection.find_one({"job_url": job_data.job_url})
            if existing:
                logger.info(f"Job already exists: {job_data.job_url}")
                return str(existing["_id"])
            
            # Create job document
            job_doc = job_data.dict()
            job_doc["created_at"] = datetime.utcnow()
            job_doc["updated_at"] = datetime.utcnow()
            
            result = self.collection.insert_one(job_doc)
            job_id = str(result.inserted_id)
            
            logger.info(f"Inserted job: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to insert job: {e}")
            return None
    
    async def get_job(self, job_id: str) -> Optional[JobPosting]:
        """Get a job posting by ID."""
        if not self.is_connected():
            return None
        
        try:
            from bson import ObjectId
            job_doc = self.collection.find_one({"_id": ObjectId(job_id)})
            if job_doc:
                return JobPosting(**job_doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    async def get_jobs(
        self,
        limit: int = 100,
        skip: int = 0,
        processed: Optional[bool] = None,
        enriched: Optional[bool] = None,
        company: Optional[str] = None,
        location: Optional[str] = None
    ) -> List[JobPosting]:
        """Get job postings with filters."""
        if not self.is_connected():
            return []
        
        try:
            # Build filter
            filter_query = {}
            if processed is not None:
                filter_query["processed"] = processed
            if enriched is not None:
                filter_query["enriched"] = enriched
            if company:
                filter_query["company"] = {"$regex": company, "$options": "i"}
            if location:
                filter_query["location"] = {"$regex": location, "$options": "i"}
            
            cursor = self.collection.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
            jobs = [JobPosting(**doc) for doc in cursor]
            
            return jobs
            
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
            return []
    
    async def update_job(self, job_id: str, update_data: JobPostingUpdate) -> bool:
        """Update a job posting."""
        if not self.is_connected():
            return False
        
        try:
            from bson import ObjectId
            
            # Prepare update data
            update_doc = update_data.dict(exclude_unset=True)
            update_doc["updated_at"] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": update_doc}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated job: {job_id}")
            else:
                logger.warning(f"No job found to update: {job_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            return False
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job posting."""
        if not self.is_connected():
            return False
        
        try:
            from bson import ObjectId
            result = self.collection.delete_one({"_id": ObjectId(job_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted job: {job_id}")
            else:
                logger.warning(f"No job found to delete: {job_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False
    
    async def get_statistics(self) -> JobStatistics:
        """Get comprehensive job statistics."""
        if not self.is_connected():
            return JobStatistics()
        
        try:
            # Basic counts
            total_jobs = self.collection.count_documents({})
            processed_jobs = self.collection.count_documents({"processed": True})
            enriched_jobs = self.collection.count_documents({"enriched": True})
            
            # Aggregation pipelines
            pipeline_seniority = [
                {"$group": {"_id": "$seniority_level", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            pipeline_work_mode = [
                {"$group": {"_id": "$work_mode", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            pipeline_company = [
                {"$group": {"_id": "$company", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 20}
            ]
            
            pipeline_location = [
                {"$group": {"_id": "$location", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 20}
            ]
            
            pipeline_skills = [
                {"$unwind": "$skills"},
                {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 50}
            ]
            
            # Execute aggregations
            seniority_results = list(self.collection.aggregate(pipeline_seniority))
            work_mode_results = list(self.collection.aggregate(pipeline_work_mode))
            company_results = list(self.collection.aggregate(pipeline_company))
            location_results = list(self.collection.aggregate(pipeline_location))
            skills_results = list(self.collection.aggregate(pipeline_skills))
            
            # Build statistics
            stats = JobStatistics(
                total_jobs=total_jobs,
                processed_jobs=processed_jobs,
                enriched_jobs=enriched_jobs,
                by_seniority={item["_id"]: item["count"] for item in seniority_results if item["_id"]},
                by_work_mode={item["_id"]: item["count"] for item in work_mode_results if item["_id"]},
                by_company={item["_id"]: item["count"] for item in company_results if item["_id"]},
                by_location={item["_id"]: item["count"] for item in location_results if item["_id"]},
                top_skills=[{"skill": item["_id"], "count": item["count"]} for item in skills_results if item["_id"]],
                skills_frequency={item["_id"]: item["count"] for item in skills_results if item["_id"]},
                last_updated=datetime.utcnow()
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return JobStatistics()
    
    async def get_companies(self) -> List[str]:
        """Get list of all companies."""
        if not self.is_connected():
            return []
        
        try:
            companies = self.collection.distinct("company")
            return sorted(companies)
        except Exception as e:
            logger.error(f"Failed to get companies: {e}")
            return []
    
    async def get_locations(self) -> List[str]:
        """Get list of all locations."""
        if not self.is_connected():
            return []
        
        try:
            locations = self.collection.distinct("location")
            return sorted(locations)
        except Exception as e:
            logger.error(f"Failed to get locations: {e}")
            return []
    
    async def get_skills(self) -> List[str]:
        """Get list of all skills."""
        if not self.is_connected():
            return []
        
        try:
            skills = self.collection.distinct("skills")
            return sorted(skills)
        except Exception as e:
            logger.error(f"Failed to get skills: {e}")
            return []


# Global database manager instance
db_manager = DatabaseManager()


async def get_database() -> DatabaseManager:
    """Get the global database manager instance."""
    return db_manager 