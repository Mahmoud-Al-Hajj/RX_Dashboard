#!/usr/bin/env python3
"""
Seed MongoDB with realistic sample job postings for the HR RemotelyX dashboard.

This script connects using environment variables defined in src.core.config.Settings
and inserts documents shaped to match what the dashboard expects to display.

Fields included per document:
- title (str)
- job_url (str, unique-ish)
- description (str)
- company (str)
- location (str)
- skills (List[str])
- seniority (str)                # used by dashboard UI
- seniority_level (str)          # used by backend analytics
- work_mode (str: Remote/Hybrid/Onsite)
- salary_min (int)
- salary_max (int)
- posting_date (datetime)
- created_at/updated_at (datetime)
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from typing import List, Dict

from pymongo import MongoClient

# Ensure project root is on sys.path for `src.*` imports
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Reuse project settings
from src.core.config import get_settings


def generate_job_documents(count: int) -> List[Dict]:
    random.seed(42)

    companies = [
        "Acme Corp",
        "Globex",
        "Initech",
        "Hooli",
        "Umbrella",
        "Stark Industries",
        "Wayne Enterprises",
        "Wonka Labs",
        "Cyberdyne",
        "Pied Piper",
    ]

    locations = [
        "New York, NY",
        "San Francisco, CA",
        "Austin, TX",
        "Seattle, WA",
        "Remote - US",
        "Chicago, IL",
        "Boston, MA",
        "Denver, CO",
        "Los Angeles, CA",
        "Miami, FL",
    ]

    titles = [
        "Software Engineer",
        "Senior Backend Engineer",
        "Frontend Developer",
        "Data Scientist",
        "ML Engineer",
        "DevOps Engineer",
        "Product Designer",
        "QA Automation Engineer",
        "Full Stack Developer",
        "Data Engineer",
    ]

    possible_skills = [
        "Python", "JavaScript", "TypeScript", "React", "Node.js", "Django", "Flask",
        "FastAPI", "MongoDB", "PostgreSQL", "SQL", "AWS", "GCP", "Azure",
        "Docker", "Kubernetes", "CI/CD", "Terraform", "Pandas", "NumPy",
        "Scikit-learn", "BeautifulSoup", "Selenium", "Plotly", "Streamlit"
    ]

    seniorities = ["Junior", "Mid", "Senior", "Lead", "Executive"]
    work_modes = ["Remote", "Hybrid", "Onsite"]

    documents: List[Dict] = []
    now = datetime.utcnow()

    for i in range(count):
        title = random.choice(titles)
        company = random.choice(companies)
        location = random.choice(locations)
        seniority = random.choices(seniorities, weights=[2, 4, 6, 2, 1], k=1)[0]
        work_mode = random.choices(work_modes, weights=[6, 3, 2], k=1)[0]

        # Skills: choose 5-10 unique skills
        skills = random.sample(possible_skills, k=random.randint(5, 10))

        # Salary bands dependent on seniority
        base_min = {
            "Junior": 60000,
            "Mid": 90000,
            "Senior": 120000,
            "Lead": 140000,
            "Executive": 180000,
        }[seniority]
        spread = 20000 if seniority in {"Junior", "Mid"} else 40000
        salary_min = base_min + random.randint(0, spread // 2)
        salary_max = salary_min + random.randint(spread // 2, spread)

        # Posting date within last 30 days
        posting_date = now - timedelta(days=random.randint(0, 30))

        job_url = f"https://example.com/jobs/{company.lower().replace(' ', '-')}/{title.lower().replace(' ', '-')}-{i}"

        description = (
            f"We are seeking a {seniority} {title} to join {company}. "
            f"You will work in a {work_mode.lower()} environment and collaborate across teams. "
            f"Experience with {', '.join(skills[:4])} is preferred."
        )

        doc = {
            "title": title,
            "job_url": job_url,
            "description": description,
            "company": company,
            "location": location,
            "skills": skills,
            # Dashboard expects 'seniority'; backend analytics may look at 'seniority_level'
            "seniority": seniority,
            "seniority_level": seniority,
            "work_mode": work_mode,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "posting_date": posting_date,
            "created_at": posting_date,
            "updated_at": now,
            # Flags used by backend stats (optional for demo)
            "processed": random.choice([True, False]),
            "enriched": random.choice([True, False]),
        }

        documents.append(doc)

    return documents


def seed_database(count: int) -> None:
    settings = get_settings()
    client = MongoClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    coll = db[settings.mongodb_collection]

    # Ensure useful indexes exist (idempotent)
    coll.create_index([("job_url", 1)], unique=True)
    coll.create_index([("title", 1)])
    coll.create_index([("company", 1)])
    coll.create_index([("location", 1)])
    coll.create_index([("skills", 1)])
    coll.create_index([("seniority", 1)])
    coll.create_index([("seniority_level", 1)])
    coll.create_index([("work_mode", 1)])
    coll.create_index([("posting_date", -1)])
    coll.create_index([("created_at", -1)])

    docs = generate_job_documents(count)

    inserted = 0
    for doc in docs:
        try:
            # Upsert on job_url so repeated runs don't create duplicates
            coll.update_one({"job_url": doc["job_url"]}, {"$set": doc}, upsert=True)
            inserted += 1
        except Exception:
            # Skip duplicates or any insertion error
            continue

    print(f"Seed completed. Upserted {inserted} documents into {settings.mongodb_database}.{settings.mongodb_collection}")


def main():
    parser = argparse.ArgumentParser(description="Seed MongoDB with sample job postings for the dashboard")
    parser.add_argument("--count", type=int, default=30, help="Number of sample jobs to insert")
    args = parser.parse_args()

    seed_database(args.count)


if __name__ == "__main__":
    main()


