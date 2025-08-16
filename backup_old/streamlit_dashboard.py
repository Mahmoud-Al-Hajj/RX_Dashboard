#!/usr/bin/env python3
"""
Streamlit Dashboard for RemotelyX Job Automation Service
Beautiful UI for managing job postings and automation workflows.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

# Page configuration
st.set_page_config(
    page_title="RemotelyX Job Automation Dashboard",
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
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .job-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-pending {
        color: #ffc107;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
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

def get_jobs():
    """Fetch jobs from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs")
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

def run_workflow(email_limit=10):
    """Run the job processing workflow"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/workflow/run",
            json={"email_limit": email_limit}
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

# Main Dashboard
def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 RemotelyX Job Automation Dashboard</h1>', unsafe_allow_html=True)
    
    # Check API connection
    if not check_api_connection():
        st.error("❌ Cannot connect to the API server. Please make sure the demo server is running with: `python demo_mode.py`")
        st.info("💡 The API server should be running on http://localhost:8000")
        return
    
    st.success("✅ Connected to RemotelyX Job Automation API")
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    
    # Workflow Controls
    st.sidebar.header("🔄 Workflow Controls")
    email_limit = st.sidebar.slider("Email Limit", 1, 50, 10)
    
    if st.sidebar.button("🚀 Run Job Processing", type="primary"):
        with st.spinner("Processing jobs..."):
            result = run_workflow(email_limit)
            if result:
                st.sidebar.success(f"✅ Processed {result['jobs_processed']} jobs")
                st.sidebar.info(f"⏱️ Duration: {result['duration']:.2f}s")
            else:
                st.sidebar.error("❌ Workflow failed")
    
    if st.sidebar.button("📊 Export to Excel"):
        with st.spinner("Exporting to Excel..."):
            result = export_to_excel()
            if result:
                st.sidebar.success(f"✅ Exported {result['exported']} jobs")
            else:
                st.sidebar.error("❌ Export failed")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📈 Dashboard Overview")
        
        # Get statistics
        stats = get_statistics()
        
        if stats:
            # Metrics row
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric(
                    label="Total Jobs",
                    value=stats.get('total_jobs_in_db', 0),
                    delta=stats.get('processed_count', 0)
                )
            
            with metric_col2:
                st.metric(
                    label="Unprocessed",
                    value=stats.get('unprocessed_jobs', 0),
                    delta_color="inverse"
                )
            
            with metric_col3:
                st.metric(
                    label="Processed",
                    value=stats.get('processed_count', 0),
                    delta=stats.get('processed_count', 0)
                )
            
            with metric_col4:
                st.metric(
                    label="Errors",
                    value=stats.get('error_count', 0),
                    delta_color="inverse"
                )
            
                    # Charts
        st.subheader("📊 Analytics")
        
        try:
            # Company distribution
            if 'excel_stats' in stats and 'companies' in stats['excel_stats']:
                companies = stats['excel_stats']['companies']
                if companies and len(companies) > 0:
                    company_df = pd.DataFrame({'Company': companies})
                    company_counts = company_df['Company'].value_counts().reset_index()
                    company_counts.columns = ['Company', 'Count']
                    if len(company_counts) > 0:
                        fig = px.bar(
                            company_counts,
                            x='Company',
                            y='Count',
                            title="Jobs by Company",
                            labels={'Company': 'Company', 'Count': 'Job Count'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            # Location distribution
            if 'excel_stats' in stats and 'locations' in stats['excel_stats']:
                locations = stats['excel_stats']['locations']
                if locations and len(locations) > 0:
                    location_df = pd.DataFrame({'Location': locations})
                    location_counts = location_df['Location'].value_counts().reset_index()
                    location_counts.columns = ['Location', 'Count']
                    if len(location_counts) > 0:
                        fig = px.pie(
                            location_counts,
                            values='Count',
                            names='Location',
                            title="Jobs by Location"
                        )
                        st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"📊 Charts could not be displayed: {str(e)}")
            st.info("💡 Run the workflow to generate data for charts")
    
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
        
        # Backup
        if st.button("💾 Create Backup"):
            try:
                response = requests.post(f"{API_BASE_URL}/excel/backup")
                if response.status_code == 200:
                    st.success("✅ Backup created successfully")
                else:
                    st.error("❌ Backup failed")
            except:
                st.error("❌ Backup failed")
        
        # Refresh data
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Jobs table
    st.header("📋 Job Postings")
    
    jobs = get_jobs()
    
    if jobs:
        # Convert to DataFrame for better display
        jobs_df = pd.DataFrame(jobs)
        
        # Format datetime columns
        if 'email_date' in jobs_df.columns:
            jobs_df['email_date'] = pd.to_datetime(jobs_df['email_date']).dt.strftime('%Y-%m-%d %H:%M')
        if 'scraped_at' in jobs_df.columns:
            jobs_df['scraped_at'] = pd.to_datetime(jobs_df['scraped_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Display jobs in a nice format
        for _, job in jobs_df.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="job-card">
                        <h3>{job.get('job_title', 'N/A')}</h3>
                        <p><strong>Company:</strong> {job.get('company', 'N/A')}</p>
                        <p><strong>Location:</strong> {job.get('location', 'N/A')}</p>
                        <p><strong>Skills:</strong> {', '.join(job.get('skills', []))}</p>
                        <p><strong>Salary:</strong> {job.get('salary', 'Not specified')}</p>
                        <p><strong>Email Subject:</strong> {job.get('email_subject', 'N/A')}</p>
                        <p><strong>Date:</strong> {job.get('email_date', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    status = "✅ Processed" if job.get('processed', False) else "⏳ Pending"
                    status_class = "status-success" if job.get('processed', False) else "status-pending"
                    st.markdown(f'<p class="{status_class}">{status}</p>', unsafe_allow_html=True)
                    
                    if st.button(f"🗑️ Delete", key=f"delete_{job.get('id', 'unknown')}"):
                        try:
                            response = requests.delete(f"{API_BASE_URL}/jobs/{job.get('id')}")
                            if response.status_code == 200:
                                st.success("✅ Job deleted")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Delete failed")
                        except:
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
        <p>🚀 RemotelyX Job Automation Dashboard | Built with Streamlit</p>
        <p>API Status: ✅ Connected | Mode: Demo</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 