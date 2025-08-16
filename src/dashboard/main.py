"""
Streamlit Dashboard for RemotelyX Job Automation Service.
Beautiful interactive dashboard for job analytics and management.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from typing import List, Dict, Any, Optional

# Page configuration
st.set_page_config(
    page_title="RemotelyX Job Intel Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .job-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
        background: #d4edda;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
    }
    .status-pending {
        color: #ffc107;
        font-weight: bold;
        background: #fff3cd;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
        background: #f8d7da;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_connection():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_jobs(limit: int = 100):
    """Fetch jobs from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs?limit={limit}")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_statistics():
    """Fetch statistics from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/statistics")
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

def run_workflow(job_urls: List[str]):
    """Run the job processing workflow"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/workflow/run",
            json=job_urls
        )
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def export_to_excel():
    """Export jobs to Excel"""
    try:
        response = requests.post(f"{API_BASE_URL}/excel/export")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def create_backup():
    """Create Excel backup"""
    try:
        response = requests.post(f"{API_BASE_URL}/excel/backup")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_companies():
    """Get list of companies"""
    try:
        response = requests.get(f"{API_BASE_URL}/companies")
        if response.status_code == 200:
            return response.json().get("companies", [])
        return []
    except:
        return []

def get_locations():
    """Get list of locations"""
    try:
        response = requests.get(f"{API_BASE_URL}/locations")
        if response.status_code == 200:
            return response.json().get("locations", [])
        return []
    except:
        return []

def get_skills():
    """Get list of skills"""
    try:
        response = requests.get(f"{API_BASE_URL}/skills")
        if response.status_code == 200:
            return response.json().get("skills", [])
        return []
    except:
        return []

def delete_job(job_id: str):
    """Delete a job"""
    try:
        response = requests.delete(f"{API_BASE_URL}/jobs/{job_id}")
        return response.status_code == 200
    except:
        return False

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 RemotelyX Job Intel Dashboard</h1>', unsafe_allow_html=True)
    
    # Check API connection
    if not check_api_connection():
        st.error("❌ Cannot connect to the API server. Please make sure the server is running.")
        st.info("💡 Start the API server with: `python -m src.api.main`")
        return
    
    st.success("✅ Connected to RemotelyX Job Automation API")
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    
    # Workflow Controls
    st.sidebar.header("🔄 Workflow Controls")
    
    # Job URL input
    st.sidebar.subheader("📝 Add Job URLs")
    job_urls_input = st.sidebar.text_area(
        "Enter job URLs (one per line):",
        height=150,
        placeholder="https://remotelyx.com/job/123\nhttps://remotelyx.com/job/456"
    )
    
    if st.sidebar.button("🚀 Run Job Processing", type="primary"):
        if job_urls_input.strip():
            urls = [url.strip() for url in job_urls_input.split('\n') if url.strip()]
            with st.spinner("Processing jobs..."):
                result = run_workflow(urls)
                if result:
                    st.sidebar.success(f"✅ Workflow started for {len(urls)} jobs")
                    st.sidebar.info("⏳ Check the dashboard for updates")
                else:
                    st.sidebar.error("❌ Workflow failed")
        else:
            st.sidebar.warning("⚠️ Please enter job URLs")
    
    # Export controls
    st.sidebar.header("📊 Export & Backup")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📊 Export to Excel"):
            with st.spinner("Exporting to Excel..."):
                result = export_to_excel()
                if result and result.get("success"):
                    st.success(f"✅ Exported {result.get('exported', 0)} jobs")
                else:
                    st.error("❌ Export failed")
    
    with col2:
        if st.button("💾 Create Backup"):
            with st.spinner("Creating backup..."):
                result = create_backup()
                if result and result.get("success"):
                    st.success("✅ Backup created")
                else:
                    st.error("❌ Backup failed")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📈 Dashboard Overview")
        
        # Get statistics
        stats = get_statistics()
        
        if stats and "database" in stats:
            db_stats = stats["database"]
            
            # Metrics row
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Jobs</h3>
                    <h2>{db_stats.get('total_jobs', 0)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Processed</h3>
                    <h2>{db_stats.get('processed_jobs', 0)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Enriched</h3>
                    <h2>{db_stats.get('enriched_jobs', 0)}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Companies</h3>
                    <h2>{len(db_stats.get('by_company', {}))}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts
            st.subheader("📊 Analytics")
            
            # Create tabs for different charts
            chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs([
                "🏢 Companies", "📍 Locations", "💼 Seniority", "🏠 Work Mode"
            ])
            
            with chart_tab1:
                if db_stats.get('by_company'):
                    company_data = pd.DataFrame([
                        {"Company": company, "Jobs": count}
                        for company, count in db_stats['by_company'].items()
                    ])
                    fig = px.bar(
                        company_data,
                        x="Company",
                        y="Jobs",
                        title="Jobs by Company",
                        color="Jobs",
                        color_continuous_scale="viridis"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No company data available")
            
            with chart_tab2:
                if db_stats.get('by_location'):
                    location_data = pd.DataFrame([
                        {"Location": location, "Jobs": count}
                        for location, count in db_stats['by_location'].items()
                    ])
                    fig = px.pie(
                        location_data,
                        values="Jobs",
                        names="Location",
                        title="Jobs by Location"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No location data available")
            
            with chart_tab3:
                if db_stats.get('by_seniority'):
                    seniority_data = pd.DataFrame([
                        {"Seniority": level, "Jobs": count}
                        for level, count in db_stats['by_seniority'].items()
                    ])
                    fig = px.bar(
                        seniority_data,
                        x="Seniority",
                        y="Jobs",
                        title="Jobs by Seniority Level",
                        color="Jobs",
                        color_continuous_scale="plasma"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No seniority data available")
            
            with chart_tab4:
                if db_stats.get('by_work_mode'):
                    work_mode_data = pd.DataFrame([
                        {"Work Mode": mode, "Jobs": count}
                        for mode, count in db_stats['by_work_mode'].items()
                    ])
                    fig = px.pie(
                        work_mode_data,
                        values="Jobs",
                        names="Work Mode",
                        title="Jobs by Work Mode"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No work mode data available")
    
    with col2:
        st.header("⚡ Quick Actions")
        
        # Health check
        if st.button("🏥 Health Check"):
            try:
                response = requests.get(f"{API_BASE_URL}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    st.success("✅ Service Healthy")
                    st.json(health_data)
                else:
                    st.error("❌ Service Unhealthy")
            except:
                st.error("❌ Cannot connect to service")
        
        # Refresh data
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        # Filter options
        st.subheader("🔍 Filters")
        
        companies = get_companies()
        locations = get_locations()
        skills = get_skills()
        
        selected_companies = st.multiselect("Companies", companies)
        selected_locations = st.multiselect("Locations", locations)
        selected_skills = st.multiselect("Skills", skills)
        
        if st.button("Apply Filters"):
            st.info("Filter functionality will be implemented in the next version")
    
    # Jobs table
    st.header("📋 Job Postings")
    
    # Get jobs
    jobs = get_jobs(limit=50)  # Limit for performance
    
    if jobs:
        # Convert to DataFrame for better display
        jobs_df = pd.DataFrame(jobs)
        
        # Format datetime columns
        datetime_columns = ['created_at', 'updated_at', 'scraped_at', 'posting_date']
        for col in datetime_columns:
            if col in jobs_df.columns:
                jobs_df[col] = pd.to_datetime(jobs_df[col]).dt.strftime('%Y-%m-%d %H:%M')
        
        # Display jobs in a nice format
        for _, job in jobs_df.iterrows():
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="job-card">
                        <h3>{job.get('title', 'N/A')}</h3>
                        <p><strong>Company:</strong> {job.get('company', 'N/A')}</p>
                        <p><strong>Location:</strong> {job.get('location', 'N/A')}</p>
                        <p><strong>Employment Type:</strong> {job.get('employment_type', 'N/A')}</p>
                        <p><strong>Seniority:</strong> {job.get('seniority_level', 'N/A')}</p>
                        <p><strong>Work Mode:</strong> {job.get('work_mode', 'N/A')}</p>
                        <p><strong>Skills:</strong> {', '.join(job.get('skills', []))}</p>
                        <p><strong>Salary:</strong> {job.get('salary_min', 'N/A')} - {job.get('salary_max', 'N/A')} {job.get('salary_currency', 'USD')}</p>
                        <p><strong>Posted:</strong> {job.get('posting_date', 'N/A')}</p>
                        <p><strong>URL:</strong> <a href="{job.get('job_url', '#')}" target="_blank">View Job</a></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Status indicators
                    processed_status = "✅ Processed" if job.get('processed', False) else "⏳ Pending"
                    enriched_status = "✅ Enriched" if job.get('enriched', False) else "⏳ Not Enriched"
                    
                    status_class = "status-success" if job.get('processed', False) else "status-pending"
                    st.markdown(f'<p class="{status_class}">{processed_status}</p>', unsafe_allow_html=True)
                    
                    enriched_class = "status-success" if job.get('enriched', False) else "status-pending"
                    st.markdown(f'<p class="{enriched_class}">{enriched_status}</p>', unsafe_allow_html=True)
                    
                    # Delete button
                    if st.button(f"🗑️ Delete", key=f"delete_{job.get('id', 'unknown')}"):
                        if delete_job(job.get('id')):
                            st.success("✅ Job deleted")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Delete failed")
        
        # Show raw data option
        with st.expander("📊 View Raw Data"):
            st.dataframe(jobs_df)
            
    else:
        st.info("📭 No jobs found. Run the workflow to process some jobs!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🚀 RemotelyX Job Intel Dashboard | Built with Streamlit</p>
        <p>API Status: ✅ Connected | Version: 1.0.0</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 