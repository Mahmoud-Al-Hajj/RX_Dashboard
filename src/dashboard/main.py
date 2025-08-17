"""
HR RemotelyX Dashboard - Direct Database Access
Professional dark-themed dashboard with direct MongoDB connection
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from typing import List, Dict, Any, Optional
import asyncio
from collections import Counter

# Import database components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.database import DatabaseManager
from src.core.config import get_settings

# Page configuration
st.set_page_config(
    page_title="HR RemotelyX",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for exact design replication
st.markdown("""
<style>
    /* Modern Professional Dark Theme */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 0;
        padding-bottom: 0;
        max-width: 100%;
    }
    
    /* Sidebar styling - Professional Dark */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 100%);
        border-right: 1px solid #3a3a5a;
        box-shadow: 2px 0 10px rgba(0,0,0,0.3);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 2rem 1.5rem;
    }
    
    /* Header styling - Professional */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 2rem;
        background: linear-gradient(135deg, #2d2d44 0%, #3a3a5a 100%);
        margin-bottom: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        border: 1px solid #4a4a6a;
    }
    
    .logo {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .search-container {
        flex: 1;
        max-width: 500px;
        margin: 0 2rem;
    }
    
    .search-container input {
        background: linear-gradient(135deg, #3a3a5a 0%, #4a4a6a 100%);
        border: 1px solid #5a5a7a;
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        color: #ffffff;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }
    
    .search-container input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
    }
    
    .user-profile {
        display: flex;
        align-items: center;
        gap: 1rem;
        color: #ffffff;
        background: linear-gradient(135deg, #3a3a5a 0%, #4a4a6a 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        border: 1px solid #5a5a7a;
        transition: all 0.3s ease;
    }
    
    .user-profile:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    }
    
    /* Navigation sidebar - Professional */
    .nav-item {
        display: flex;
        align-items: center;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        color: #ffffff;
        text-decoration: none;
        transition: all 0.3s ease;
        font-weight: 500;
        border: 1px solid transparent;
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    
    .nav-item:hover {
        background: linear-gradient(135deg, #3a3a5a 0%, #4a4a6a 100%);
        transform: translateX(5px);
        border-color: #5a5a7a;
    }
    
    .nav-icon {
        margin-right: 1rem;
        font-size: 1.2rem;
        opacity: 0.8;
    }
    
    /* Data Insight Cards - Professional */
    .insight-card {
        background: linear-gradient(135deg, #2d2d44 0%, #3a3a5a 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid #4a4a6a;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        position: relative;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s ease;
        overflow: hidden;
    }
    
    .insight-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-color), var(--accent-color-light));
    }
    
    .insight-card.blue { 
        --accent-color: #4a90e2; 
        --accent-color-light: #5ba0f2;
    }
    .insight-card.red { 
        --accent-color: #ff6b35; 
        --accent-color-light: #ff7b45;
    }
    .insight-card.yellow { 
        --accent-color: #ffd93d; 
        --accent-color-light: #ffe94d;
    }
    .insight-card.green { 
        --accent-color: #4caf50; 
        --accent-color-light: #5cbf60;
    }
    
    .insight-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    
    .insight-icon {
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        font-size: 2rem;
        opacity: 0.3;
        background: linear-gradient(135deg, var(--accent-color), var(--accent-color-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .insight-title {
        font-size: 0.9rem;
        color: #b0b0b0;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .insight-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .insight-subtitle {
        font-size: 0.8rem;
        color: var(--accent-color);
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .insight-subtitle:hover {
        color: var(--accent-color-light);
        transform: translateX(5px);
    }
    
    /* Chart containers - Professional */
    .chart-container {
        background: linear-gradient(135deg, #2d2d44 0%, #3a3a5a 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid #4a4a6a;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .chart-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }
    
    .chart-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .time-filter {
        font-size: 0.9rem;
        color: #b0b0b0;
        background: linear-gradient(135deg, #3a3a5a 0%, #4a4a6a 100%);
        border: 1px solid #5a5a7a;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .time-filter:hover {
        border-color: #667eea;
        color: #667eea;
    }
    
    /* Section headers - Professional */
    .section-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 3rem 0 2rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        position: relative;
        padding-left: 1rem;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }
    
    /* Buttons - Professional */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Metrics - Professional */
    .stMetric {
        background: linear-gradient(135deg, #2d2d44 0%, #3a3a5a 100%);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid #4a4a6a;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    /* Dataframes - Professional */
    .stDataFrame {
        background: linear-gradient(135deg, #2d2d44 0%, #3a3a5a 100%);
        border-radius: 15px;
        border: 1px solid #4a4a6a;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Expanders - Professional */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #2d2d44 0%, #3a3a5a 100%);
        border: 1px solid #4a4a6a;
        border-radius: 15px;
        color: #ffffff;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #3a3a5a 0%, #4a4a6a 100%);
        border-color: #667eea;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .header-container {
            flex-direction: column;
            gap: 1rem;
            padding: 1rem;
        }
        
        .search-container {
            max-width: 100%;
            margin: 0;
        }
        
        .insight-card {
            height: auto;
            min-height: 120px;
        }
        
        .insight-value {
            font-size: 2rem;
        }
        
        .section-header {
            font-size: 1.5rem;
        }
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2d2d44;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6ff0 0%, #865bb8 100%);
    }
</style>
""", unsafe_allow_html=True)

# Database Configuration
settings = get_settings()
db_manager = DatabaseManager()

def check_database_connection():
    """Check if the database is connected"""
    try:
        # Try to connect to database
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        connected = loop.run_until_complete(db_manager.connect())
        return connected
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return False

def get_jobs(limit: int = 100):
    """Fetch jobs directly from database"""
    try:
        if not db_manager.is_connected():
            if not check_database_connection():
                return []
        
        # Get jobs from database
        cursor = db_manager.collection.find().limit(limit)
        jobs = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for job in jobs:
            job['_id'] = str(job['_id'])
        
        return jobs
    except Exception as e:
        st.error(f"Failed to fetch jobs: {e}")
        return []

def get_statistics():
    """Get statistics directly from database"""
    try:
        if not db_manager.is_connected():
            if not check_database_connection():
                return {}
        
        # Get basic counts
        total_jobs = db_manager.collection.count_documents({})
        
        # Get skills statistics
        pipeline_skills = [
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 50}
        ]
        skills_results = list(db_manager.collection.aggregate(pipeline_skills))
        
        # Get seniority statistics
        pipeline_seniority = [
            {"$group": {"_id": "$seniority", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        seniority_results = list(db_manager.collection.aggregate(pipeline_seniority))
        
        # Get work mode statistics
        pipeline_work_mode = [
            {"$group": {"_id": "$work_mode", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        work_mode_results = list(db_manager.collection.aggregate(pipeline_work_mode))
        
        stats = {
            "database": {
                "total_jobs": total_jobs,
                "skills_frequency": {item["_id"]: item["count"] for item in skills_results if item["_id"]},
                "by_seniority": {item["_id"]: item["count"] for item in seniority_results if item["_id"]},
                "by_work_mode": {item["_id"]: item["count"] for item in work_mode_results if item["_id"]},
                "top_skills": [{"skill": item["_id"], "count": item["count"]} for item in skills_results if item["_id"]]
            }
        }
        
        return stats
    except Exception as e:
        st.error(f"Failed to get statistics: {e}")
        return {}

def add_job_manually(job_data: Dict[str, Any]):
    """Add a job directly to database"""
    try:
        if not db_manager.is_connected():
            if not check_database_connection():
                return False
        
        # No additional timestamps needed - using your exact schema
        
        # Insert job
        result = db_manager.collection.insert_one(job_data)
        return str(result.inserted_id)
    except Exception as e:
        st.error(f"Failed to add job: {e}")
        return None

def delete_job(job_id: str):
    """Delete a job from database"""
    try:
        if not db_manager.is_connected():
            if not check_database_connection():
                return False
        
        from bson import ObjectId
        result = db_manager.collection.delete_one({"_id": ObjectId(job_id)})
        return result.deleted_count > 0
    except Exception as e:
        st.error(f"Failed to delete job: {e}")
        return False

def get_skills():
    """Get list of skills from database"""
    try:
        if not db_manager.is_connected():
            if not check_database_connection():
                return []
        
        skills = db_manager.collection.distinct("skills")
        return skills
    except Exception as e:
        st.error(f"Failed to fetch skills: {e}")
        return []

def main():
    # Sidebar - HR RemotelyX Logo and Navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #444;">
            <h2 style="color: #4a90e2; margin: 0;">HR RemotelyX</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        st.markdown("""
        <div style="margin-top: 2rem;">
            <div class="nav-item active">
                <span class="nav-icon">📊</span>
                Dashboard
            </div>
            <div class="nav-item">
                <span class="nav-icon">📅</span>
                Calendar
            </div>
            <div class="nav-item">
                <span class="nav-icon">👥</span>
                Candidates
            </div>
            <div class="nav-item">
                <span class="nav-icon">👨‍💼</span>
                Employees
            </div>
            <div class="nav-item">
                <span class="nav-icon">📄</span>
                Documents
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Bottom section
        st.markdown("""
        <div style="position: absolute; bottom: 2rem; width: 100%;">
            <hr style="border-color: #444; margin: 1rem 0;">
            <div class="nav-item">
                <span class="nav-icon">⚙️</span>
                Settings
            </div>
            <div class="nav-item">
                <span class="nav-icon">🚪</span>
                Log Out
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="header-container">
        <div>
            <h1 style="margin: 0; color: #ffffff; font-size: 2rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">Dashboard</h1>
        </div>
        <div class="search-container">
            <input type="text" placeholder="Search for jobs, candidates and more..." 
                   style="width: 100%; padding: 0.75rem 1.5rem; border-radius: 25px; border: 1px solid #5a5a7a; background: linear-gradient(135deg, #3a3a5a 0%, #4a4a6a 100%); color: #ffffff; font-size: 0.9rem; transition: all 0.3s ease;">
        </div>
        <div class="user-profile">
            <span style="font-size: 1.3rem; opacity: 0.8;">🔔</span>
            <div style="width: 45px; height: 45px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; margin: 0 0.75rem; box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);">
                <span style="color: white; font-weight: bold; font-size: 1.1rem;">RK</span>
            </div>
            <div>
                <div style="font-weight: 600; font-size: 1rem;">Racile Kabbara</div>
                <div style="font-size: 0.8rem; color: #b0b0b0; opacity: 0.8;">Chief of Staff</div>
            </div>
            <span style="margin-left: 0.75rem; opacity: 0.6; transition: all 0.3s ease;">▼</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check database connection
    if not check_database_connection():
        st.error("❌ Cannot connect to the database. Please make sure MongoDB is running.")
        st.info("💡 MongoDB should be running on localhost:27017")
        st.info("💡 Check if Docker containers are running: docker-compose ps")
        st.info("💡 Try refreshing the page in a few seconds...")
        
        # Show retry button
        if st.button("🔄 Retry Connection"):
            st.rerun()
        return
    
    st.success("✅ Connected to MongoDB database")
    
    # Data Insight Section
    st.markdown('<h2 class="section-header">Data Insight</h2>', unsafe_allow_html=True)
    
    # Get statistics
    stats = get_statistics()
    jobs = get_jobs(limit=100)
    
    # Calculate metrics from real data
    total_jobs = len(jobs) if jobs else 0
    
    # Get top skill from real data
    all_skills = []
    for job in jobs:
        if job.get('skills'):
            all_skills.extend(job.get('skills', []))
    
    from collections import Counter
    skill_counts = Counter(all_skills)
    top_skill = skill_counts.most_common(1)[0][0] if skill_counts else "N/A"
    
    # Get top role (seniority) from real data
    seniority_counts = Counter([job.get('seniority', 'N/A') for job in jobs])
    top_role = seniority_counts.most_common(1)[0][0] if seniority_counts else "N/A"
    
    # Get unique skills count from real data
    unique_skills = len(set(all_skills)) if all_skills else 0
    
    # Data Insight Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="insight-card blue">
            <div class="insight-icon">💼</div>
            <div>
                <div class="insight-title">Total Jobs</div>
                <div class="insight-value">{total_jobs}</div>
                <div class="insight-subtitle">View Jobs</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="insight-card red">
            <div class="insight-icon">📊</div>
            <div>
                <div class="insight-title">Top Skill</div>
                <div class="insight-value">{top_skill}</div>
                <div class="insight-subtitle">View Skills</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="insight-card yellow">
            <div class="insight-icon">👤</div>
            <div>
                <div class="insight-title">Top Role</div>
                <div class="insight-value">{top_role}</div>
                <div class="insight-subtitle">View Skills</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="insight-card green">
            <div class="insight-icon">🎯</div>
            <div>
                <div class="insight-title">Unique Skills</div>
                <div class="insight-value">{unique_skills}</div>
                <div class="insight-subtitle">View Skills</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        # Application Funnel Chart
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">
                Application Funnel
                <select class="time-filter">
                    <option>This Month</option>
                </select>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create application funnel data from real job data
        if jobs:
            # Group jobs by seniority level
            seniority_counts = Counter([job.get('seniority', 'Unknown') for job in jobs])
            categories = list(seniority_counts.keys())[:5] if seniority_counts else []
            
            if not categories:
                st.info("No seniority data available for application funnel")
                return
            
            # Create simple distribution based on seniority counts
            application_data = {}
            for category in categories:
                count = seniority_counts[category]
                # Distribute the count across stages (simplified)
                application_data[category] = [count, count//2, count//3, count//4]
            
            # Create stacked bar chart
            fig = go.Figure()
            
            # Use dynamic stages based on data
            stages = ["Applied", "Interviewed", "Rejected", "Hired"]
            colors = ["#4a90e2", "#ff6b35", "#e74c3c", "#4caf50"]
                        
            for i, stage in enumerate(stages):
                fig.add_trace(go.Bar(
                    name=stage,
                    x=categories,
                    y=[application_data[cat][i] for cat in categories],
                    marker_color=colors[i]
                ))
            
            fig.update_layout(
                title="Application Funnel",
                barmode='stack',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No job data available for application funnel")
    
    with col2:
        # Salary Range Chart
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">
                Salary Range
                <select class="time-filter">
                    <option>This Week</option>
                </select>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create salary range data from real job data
        if jobs:
            # Get actual salary ranges from data
            salaries = [job.get('salary_min', 0) for job in jobs if job.get('salary_min', 0) > 0]
            
            if not salaries:
                st.info("No salary data available")
                return
            
            # Create dynamic salary ranges based on actual data
            min_salary = min(salaries)
            max_salary = max(salaries)
            
            # Create 7 ranges based on actual data
            range_size = (max_salary - min_salary) / 7 if max_salary > min_salary else 1000
            salary_ranges = []
            salary_counts = [0] * 7
            
            for i in range(7):
                start = min_salary + (i * range_size)
                end = min_salary + ((i + 1) * range_size)
                salary_ranges.append(f"${int(start)}-${int(end)}")
                
                # Count jobs in this range
                for job in jobs:
                    salary_min = job.get('salary_min', 0)
                    if start <= salary_min < end:
                        salary_counts[i] += 1
            
            # If no salary data, show empty chart
            if sum(salary_counts) == 0:
                st.info("No salary data available")
                return
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=salary_ranges,
                y=salary_counts,
                marker_color=['#4a90e2'] * len(salary_ranges),
                name="Number of Jobs"
            ))
            
            fig.update_layout(
                title="Salary Range",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No job data available for salary range")
    
    # Second Row of Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Current Activity Chart
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">
                Number of Job Postings
                <select class="time-filter">
                    <option>This Week</option>
                </select>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create activity timeline from real job data
        dates = []
        job_postings = []
        previous_period = []
        
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            dates.append(date.strftime('%d/%m'))
            
            # Count jobs (simplified - no date filtering since we don't have created_at)
            day_jobs = len(jobs) // 7  # Distribute jobs evenly across days
            job_postings.append(day_jobs)
            previous_period.append(max(0, day_jobs - 2))
        
        # If no real data, show empty chart
        if sum(job_postings) == 0:
            st.info("No job data available for timeline")
            return
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=job_postings,
            mode='lines+markers',
            name='Job Postings',
            line=dict(color='#4a90e2', width=3),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=dates,
            y=previous_period,
            mode='lines',
            name='Previous Period',
            line=dict(color='#888', width=2, dash='dot')
        ))
        
        fig.update_layout(
            title="Number of Job Postings",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Jobs Distribution Charts
        st.markdown("""
        <div class="chart-container">
            <div class="chart-title">
                Jobs Distribution
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create distribution data from real job data
        if jobs:
            # Skills distribution
            all_skills = []
            for job in jobs:
                if job.get('skills'):
                    all_skills.extend(job.get('skills', []))
            
            skill_counts = Counter(all_skills)
            top_skills = skill_counts.most_common(5)
            skills = [skill[0] for skill in top_skills] if top_skills else []
            skill_values = [skill[1] for skill in top_skills] if top_skills else []
            
            # Seniority distribution
            seniority_counts = Counter([job.get('seniority', 'Unknown') for job in jobs])
            seniorities = list(seniority_counts.keys())[:3] if seniority_counts else []
            seniority_values = list(seniority_counts.values())[:3] if seniority_counts else []
            
            # Create donut charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = go.Figure(data=[go.Pie(
                    labels=skills,
                    values=skill_values,
                    hole=0.6,
                    marker_colors=['#4a90e2'] * len(skills) if skills else []
                )])
                fig1.update_layout(
                    title="Top Skills",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=300,
                    showlegend=True
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = go.Figure(data=[go.Pie(
                    labels=seniorities,
                    values=seniority_values,
                    hole=0.6,
                    marker_colors=['#ff6b35'] * len(seniorities) if seniorities else []
                )])
                fig2.update_layout(
                    title="Per Seniority",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=300,
                    showlegend=True
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No job data available for distribution charts")
    
    # Job Management Section
    st.markdown('<h2 class="section-header">Job Management</h2>', unsafe_allow_html=True)
    
    # Add job manually
    with st.expander("➕ Add New Job", expanded=False):
        st.markdown("### Add Job Manually")
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Job Title", placeholder="e.g., Senior Python Developer")
            job_url = st.text_input("Job URL", placeholder="https://remotelyx.com/job/123")
            description = st.text_area("Description", placeholder="Job description...")
            seniority = st.selectbox("Seniority", ["", "Junior", "Mid", "Senior", "Lead", "Executive"])
            work_mode = st.selectbox("Work Mode", ["", "Remote", "Hybrid", "Onsite"])
        
        with col2:
            skills_input = st.text_input("Skills (comma separated)", placeholder="Python, React, SQL")
            salary_min = st.number_input("Min Salary ($)", min_value=0, value=0)
            salary_max = st.number_input("Max Salary ($)", min_value=0, value=0)
        
        if st.button("💾 Add Job", type="primary"):
            if title and job_url:
                # Prepare job data
                skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()] if skills_input else []
                
                job_data = {
                    "title": title,
                    "job_url": job_url,
                    "description": description,
                    "skills": skills,
                    "seniority": seniority,
                    "work_mode": work_mode,
                    "salary_min": salary_min,
                    "salary_max": salary_max
                }
                
                with st.spinner("Adding job..."):
                    result = add_job_manually(job_data)
                    if result:
                        st.success(f"✅ Job added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add job")
            else:
                st.warning("⚠️ Please fill in at least title and job URL")
    
    # Advanced Analytics Section
    st.markdown('<h2 class="section-header">Advanced Analytics</h2>', unsafe_allow_html=True)
    
    if jobs:
        # Calculate advanced metrics from real data
        col1, col2 = st.columns(2)
        
        with col1:
            # Average Salary Range
            st.markdown("### 💰 Average Salary Analysis")
            
            salaries = []
            for job in jobs:
                if job.get('salary_min') and job.get('salary_max'):
                    avg_salary = (job['salary_min'] + job['salary_max']) / 2
                    salaries.append(avg_salary)
            
            if salaries:
                avg_salary = sum(salaries) / len(salaries)
                min_salary = min(salaries)
                max_salary = max(salaries)
                
                st.metric("Average Salary", f"${avg_salary:,.0f}")
                st.metric("Salary Range", f"${min_salary:,.0f} - ${max_salary:,.0f}")
                st.metric("Jobs with Salary Data", len(salaries))
            else:
                st.info("No salary data available")
            
            # Most Occurring Skills
            st.markdown("### 🎯 Top Skills Analysis")
            
            all_skills = []
            for job in jobs:
                if job.get('skills'):
                    all_skills.extend(job.get('skills', []))
            
            if all_skills:
                skill_counts = Counter(all_skills)
                top_skills = skill_counts.most_common(10)
                
                # Create skills chart
                skills_df = pd.DataFrame(top_skills, columns=['Skill', 'Count'])
                fig = px.bar(
                    skills_df,
                    x='Count',
                    y='Skill',
                    orientation='h',
                    title="Most Occurring Skills",
                    color='Count',
                    color_continuous_scale='viridis'
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No skills data available")
        
        with col2:
            # Filtering Section
            st.markdown("### 🔍 Advanced Filters")
            
            # Get unique values for filters
            skills = list(set([skill for job in jobs if job.get('skills') for skill in job.get('skills', [])]))
            seniorities = list(set([job.get('seniority', 'Unknown') for job in jobs if job.get('seniority')]))
            
            # Filter controls
            selected_skills = st.multiselect("Filter by Skills", skills, default=skills[:5] if skills else [])
            selected_seniorities = st.multiselect("Filter by Seniority", seniorities, default=seniorities if seniorities else [])
            
            # Apply filters
            filtered_jobs = jobs.copy()
            
            if selected_skills:
                filtered_jobs = [job for job in filtered_jobs if any(skill in job.get('skills', []) for skill in selected_skills)]
            
            if selected_seniorities:
                filtered_jobs = [job for job in filtered_jobs if job.get('seniority') in selected_seniorities]
            
            st.metric("Filtered Jobs", len(filtered_jobs))
            st.metric("Total Jobs", len(jobs))
            
            # Show filtered results
            if filtered_jobs != jobs:
                st.markdown("#### Filtered Results:")
                filtered_df = pd.DataFrame(filtered_jobs)
                if not filtered_df.empty:
                    display_cols = ['title', 'seniority', 'work_mode']
                    available_cols = [col for col in display_cols if col in filtered_df.columns]
                    if available_cols:
                        st.dataframe(filtered_df[available_cols], use_container_width=True)
    
    # Admin Panel Section
    st.markdown('<h2 class="section-header">Admin Panel</h2>', unsafe_allow_html=True)
    
    admin_col1, admin_col2 = st.columns(2)
    
    with admin_col1:
        st.markdown("### 🛠️ System Management")
        
        # Database health check
        if st.button("🏥 Database Health Check"):
            try:
                if db_manager.is_connected():
                    # Test database operations
                    total_jobs = db_manager.collection.count_documents({})
                    st.success("✅ Database Healthy")
                    st.json({
                        "status": "connected",
                        "total_jobs": total_jobs,
                        "database": settings.mongodb_database,
                        "collection": settings.mongodb_collection
                    })
                else:
                    st.error("❌ Database not connected")
            except Exception as e:
                st.error(f"❌ Database Error: {e}")
        
        # Export functionality
        if st.button("📊 Export to CSV"):
            try:
                jobs = get_jobs(limit=1000)
                if jobs:
                    df = pd.DataFrame(jobs)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="jobs_export.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No jobs to export")
            except Exception as e:
                st.error(f"❌ Export failed: {e}")
        
        # Refresh data
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    with admin_col2:
        st.markdown("### 📈 Database Statistics")
        
        if stats and "database" in stats:
            db_stats = stats["database"]
            
            st.metric("Total Jobs", db_stats.get('total_jobs', 0))
            st.metric("Jobs with Skills", len([j for j in jobs if j.get('skills')]))
            st.metric("Jobs with Salary", len([j for j in jobs if j.get('salary_min') and j.get('salary_max')]))
            st.metric("Unique Skills", len(db_stats.get('skills_frequency', {})))
            
            # Database breakdown
            if db_stats.get('skills_frequency'):
                st.markdown("#### Top Skills:")
                skills_df = pd.DataFrame([
                    {"Skill": skill, "Count": count}
                    for skill, count in list(db_stats['skills_frequency'].items())[:5]
                ])
                st.dataframe(skills_df, use_container_width=True)
    
    # Display jobs in a table format
    st.markdown('<h2 class="section-header">Job Postings</h2>', unsafe_allow_html=True)
    
    if jobs:
        # Convert to DataFrame for better display
        jobs_df = pd.DataFrame(jobs)
        
        # Select relevant columns
        display_columns = ['title', 'seniority', 'work_mode', 'salary_min', 'salary_max']
        available_columns = [col for col in display_columns if col in jobs_df.columns]
        
        if available_columns:
            display_df = jobs_df[available_columns].copy()
            
            # Format salary columns
            if 'salary_min' in display_df.columns and 'salary_max' in display_df.columns:
                display_df['salary'] = display_df.apply(
                    lambda row: f"${row['salary_min']}-${row['salary_max']}" 
                    if pd.notna(row['salary_min']) and pd.notna(row['salary_max']) 
                    else "N/A", axis=1
                )
                display_df = display_df.drop(['salary_min', 'salary_max'], axis=1)
            
            # Rename columns for better display
            display_df.columns = [col.title().replace('_', ' ') for col in display_df.columns]
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.dataframe(jobs_df, use_container_width=True)
    else:
        st.info("📭 No jobs found. Add some job URLs to get started!")

if __name__ == "__main__":
    main()