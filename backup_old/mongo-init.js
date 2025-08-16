// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the remotelyx_jobs database
db = db.getSiblingDB('remotelyx_jobs');

// Create the job_postings collection
db.createCollection('job_postings');

// Create indexes for better performance
db.job_postings.createIndex({ "job_url": 1 }, { unique: true });
db.job_postings.createIndex({ "email_date": -1 });
db.job_postings.createIndex({ "processed": 1 });
db.job_postings.createIndex({ "company": 1 });
db.job_postings.createIndex({ "location": 1 });
db.job_postings.createIndex({ "scraped_at": -1 });

// Create a user for the application (optional, for additional security)
db.createUser({
    user: "remotelyx_user",
    pwd: "remotelyx_password",
    roles: [
        {
            role: "readWrite",
            db: "remotelyx_jobs"
        }
    ]
});

print("MongoDB initialization completed successfully");
print("Database: remotelyx_jobs");
print("Collection: job_postings");
print("Indexes created: job_url (unique), email_date, processed, company, location, scraped_at"); 