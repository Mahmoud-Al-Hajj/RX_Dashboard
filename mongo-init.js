// MongoDB initialization script for RemotelyX Job Automation Service

// Create the database and user
db = db.getSiblingDB("remotelyx_jobs");

// Create a user for the application
db.createUser({
  user: "remotelyx_user",
  pwd: "remotelyx_pass",
  roles: [
    {
      role: "readWrite",
      db: "remotelyx_jobs",
    },
  ],
});

// Create the job_postings collection
db.createCollection("job_postings");

// Create indexes for better performance
db.job_postings.createIndex({ title: 1 });
db.job_postings.createIndex({ company: 1 });
db.job_postings.createIndex({ location: 1 });
db.job_postings.createIndex({ job_url: 1 }, { unique: true });
db.job_postings.createIndex({ posting_date: -1 });
db.job_postings.createIndex({ created_at: -1 });
db.job_postings.createIndex({ processed: 1 });
db.job_postings.createIndex({ enriched: 1 });
db.job_postings.createIndex({ skills: 1 });
db.job_postings.createIndex({ seniority_level: 1 });
db.job_postings.createIndex({ work_mode: 1 });

// Insert some sample data for testing
db.job_postings.insertMany([
  {
    title: "Senior Software Engineer",
    company: "TechCorp Inc",
    location: "San Francisco, CA",
    job_url: "https://remotelyx.com/job/sample1",
    description:
      "We are looking for a senior software engineer with Python and React experience.",
    skills: ["Python", "React", "JavaScript", "MongoDB"],
    tags: ["Engineering", "Full-stack", "Remote"],
    employment_type: "Full-time",
    seniority_level: "Senior",
    work_mode: "Remote",
    salary_min: 120000,
    salary_max: 180000,
    salary_currency: "USD",
    salary_period: "year",
    posting_date: new Date("2024-01-15"),
    scraped_at: new Date(),
    processed: true,
    enriched: true,
    created_at: new Date(),
    updated_at: new Date(),
  },
  {
    title: "Frontend Developer",
    company: "StartupXYZ",
    location: "New York, NY",
    job_url: "https://remotelyx.com/job/sample2",
    description:
      "Join our team as a frontend developer working with modern web technologies.",
    skills: ["JavaScript", "React", "CSS", "HTML"],
    tags: ["Frontend", "Web Development", "Startup"],
    employment_type: "Full-time",
    seniority_level: "Mid",
    work_mode: "Hybrid",
    salary_min: 80000,
    salary_max: 120000,
    salary_currency: "USD",
    salary_period: "year",
    posting_date: new Date("2024-01-16"),
    scraped_at: new Date(),
    processed: true,
    enriched: true,
    created_at: new Date(),
    updated_at: new Date(),
  },
]);

print("RemotelyX database initialized successfully!");
print("Sample data inserted for testing.");
