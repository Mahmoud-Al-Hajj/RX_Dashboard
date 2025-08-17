// MongoDB initialization script for RemotelyX Job Automation Service

// Switch to the database (creates it if it doesn't exist)
db = db.getSiblingDB("remotelyx_jobs");

// Create the job_postings collection
if (!db.getCollectionNames().includes("job_postings")) {
  db.createCollection("job_postings");
}

// Create indexes only for the specified fields
db.job_postings.createIndex({ title: 1 });
db.job_postings.createIndex({ job_url: 1 }, { unique: true });
db.job_postings.createIndex({ skills: 1 });
db.job_postings.createIndex({ seniority: 1 });
db.job_postings.createIndex({ work_mode: 1 });
db.job_postings.createIndex({ salary_min: 1 });
db.job_postings.createIndex({ salary_max: 1 });

print("RemotelyX database initialized successfully!");
print(
  "Indexes created for: title, job_url, skills, seniority, work_mode, salary_min, salary_max"
);

// -----------------------------------------------------
// Cleanup step: normalize existing messy documents
// -----------------------------------------------------
db.job_postings.find().forEach((doc) => {
  if (!doc) return;

  // Skip if already structured (skills is an array)
  if (Array.isArray(doc.skills)) return;

  // Extract structured fields if they exist
  let cleanDoc = {
    title: doc.title || "",
    job_url: doc.job_url || "",
    description: doc.description || "",
    skills: [],
    seniority: doc.seniority || "",
    work_mode: doc.work_mode || "",
    salary_min: doc.salary_min || "",
    salary_max: doc.salary_max || "",
  };

  // Detect messy keys with null values (skills & garbage)
  let skillCandidates = Object.keys(doc)
    .filter((k) => doc[k] === null) // only keep null keys
    .map((k) => k.trim());

  // Keep only clean words/phrases as skills
  let skills = skillCandidates.filter((k) => /^[A-Za-z\s]+$/.test(k));

  if (skills.length > 0) {
    cleanDoc.skills = skills;
  }

  // Update the document in place
  db.job_postings.updateOne({ _id: doc._id }, { $set: cleanDoc });
});

print("Cleanup complete: existing job postings normalized.");

// -----------------------------------------------------
// Insert function for future job postings
// -----------------------------------------------------
function insertJobPosting(rawText) {
  rawText = rawText.replace(/```json\s*|\s*```/g, "").trim();

  let cleanDoc = {
    title: "",
    job_url: "",
    description: "",
    skills: [],
    seniority: "",
    work_mode: "",
    salary_min: "",
    salary_max: "",
  };

  // Try parsing JSON
  try {
    const data = JSON.parse(rawText);
    cleanDoc.title = data.title || "";
    cleanDoc.job_url = data.job_url || "";
    cleanDoc.description = data.description || "";
    cleanDoc.seniority = data.seniority || "";
    cleanDoc.work_mode = data.work_mode || "";
    cleanDoc.salary_min = data.salary?.min || "";
    cleanDoc.salary_max = data.salary?.max || "";

    if (Array.isArray(data.skills)) {
      cleanDoc.skills = data.skills.map((s) => s.trim());
    } else if (typeof data.skills === "string") {
      cleanDoc.skills = data.skills.split(",").map((s) => s.trim());
    }
  } catch (err) {
    // Plain text fallback
    const lines = rawText.split("\n").map((l) => l.trim());
    cleanDoc.title = lines[0] || "";
    const urlMatch = rawText.match(/https?:\/\/\S+/);
    if (urlMatch) cleanDoc.job_url = urlMatch[0];

    // Skills: any short capitalized phrases
    cleanDoc.skills = lines.filter(
      (l) => /^[A-Za-z\s]+$/.test(l) && l.length < 40
    );
  }

  db.job_postings.updateOne(
    { job_url: cleanDoc.job_url },
    { $set: cleanDoc },
    { upsert: true }
  );
}

// Example usage:
// insertJobPosting("Hardware\nSoftware\nNetworking\nIT Specialist\nhttps://gamma.app/docs/IT-Specialist...");
