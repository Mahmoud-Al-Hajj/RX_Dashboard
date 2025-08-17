import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pymongo
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="HR RemotelyX Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color palette from the image
COLORS = {
    'primary_blue': '#5865F2',
    'secondary_purple': '#7C3AED', 
    'red': '#EF4444',
    'coral': '#FB7185',
    'dark_teal': '#065F46',
    'light_teal': '#14B8A6',
    'brown': '#A16207',
    'yellow': '#F59E0B',
    'gray': '#6B7280',
    'white': '#FFFFFF',
    'dark_bg': '#0F172A',
    'card_bg': '#1E293B',
    'border_color': '#334155'
}

# MongoDB connection
@st.cache_resource
def init_connection():
    """Initialize MongoDB connection"""
    try:
        # Replace with your MongoDB connection string
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["remotelyx"]
        return db
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        return None

# Load data from MongoDB
@st.cache_data
def load_data_from_mongo():
    """Load data from MongoDB collections"""
    db = init_connection()
    
    if db is None:
        # Fallback to sample data if MongoDB is not available
        return generate_sample_data()
    
    try:
        # Load data from MongoDB collections
        jobs_data = list(db.jobs.find({}))
        applications_data = list(db.applications.find({}))
        skills_data = list(db.skills.find({}))
        
        jobs_df = pd.DataFrame(jobs_data)
        applications_df = pd.DataFrame(applications_data)
        skills_df = pd.DataFrame(skills_data)
        
        return jobs_df, applications_df, skills_df
        
    except Exception as e:
        st.warning(f"Could not load from MongoDB: {e}. Using sample data.")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample data when MongoDB is not available"""
    np.random.seed(42)
    
    # Jobs data
    jobs_data = {
        'job_id': range(1, 125),
        'title': np.random.choice(['Software Engineer', 'Data Scientist', 'Product Manager', 'UX Designer', 'Marketing Manager', 'Sales Representative'], 124),
        'department': np.random.choice(['Engineering', 'Data', 'Product', 'Design', 'Marketing', 'Sales'], 124),
        'location': np.random.choice(['New York', 'San Francisco', 'Remote', 'London', 'Berlin'], 124),
        'salary_range': np.random.choice(['$60k-$80k', '$80k-$100k', '$100k-$120k', '$120k-$150k', '$150k+'], 124),
        'seniority': np.random.choice(['Junior', 'Mid', 'Senior'], 124),
        'status': np.random.choice(['Open', 'Filled', 'On Hold'], 124),
        'posted_date': [datetime.now() - timedelta(days=np.random.randint(1, 180)) for _ in range(124)]
    }
    
    # Applications data
    applications_data = {
        'app_id': range(1, 116),
        'job_id': np.random.choice(range(1, 125), 115),
        'candidate_name': [f'Candidate {i}' for i in range(1, 116)],
        'stage': np.random.choice(['Applied', 'Interviewed', 'Rejected', 'Hired'], 115),
        'application_date': [datetime.now() - timedelta(days=np.random.randint(1, 90)) for _ in range(115)]
    }
    
    # Skills data
    skills_data = {
        'skill_id': range(1, 46),
        'skill_name': np.random.choice(['Python', 'JavaScript', 'React', 'SQL', 'Machine Learning', 'Project Management', 'UI/UX Design'], 45),
        'demand_count': np.random.randint(5, 50, 45)
    }
    
    return pd.DataFrame(jobs_data), pd.DataFrame(applications_data), pd.DataFrame(skills_data)

# Load data
jobs_df, applications_df, skills_df = load_data_from_mongo()

# Enhanced CSS styling to match the original design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        background-color: #0F172A;
        font-family: 'Inter', sans-serif;
    }
    
    /* Main content area */
    .main {
        background-color: #0F172A;
        padding: 2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }
    
    .sidebar .sidebar-content {
        background-color: #1E293B;
        color: #F8FAFC;
    }
    
    /* Custom metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #334155;
        position: relative;
        overflow: hidden;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        border-radius: 0 4px 4px 0;
    }
    
    .metric-blue::before { background: linear-gradient(180deg, #5865F2, #7C3AED); }
    .metric-red::before { background: linear-gradient(180deg, #EF4444, #FB7185); }
    .metric-yellow::before { background: linear-gradient(180deg, #F59E0B, #FBBF24); }
    .metric-teal::before { background: linear-gradient(180deg, #14B8A6, #06B6D4); }
    
    .metric-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-bottom: 12px;
    }
    
    .metric-blue .metric-icon { background: rgba(88, 101, 242, 0.1); color: #5865F2; }
    .metric-red .metric-icon { background: rgba(239, 68, 68, 0.1); color: #EF4444; }
    .metric-yellow .metric-icon { background: rgba(245, 158, 11, 0.1); color: #F59E0B; }
    .metric-teal .metric-icon { background: rgba(20, 184, 166, 0.1); color: #14B8A6; }
    
    .metric-title {
        color: #CBD5E1;
        font-size: 14px;
        font-weight: 500;
        margin: 0;
        line-height: 1.2;
    }
    
    .metric-value {
        color: #F8FAFC;
        font-size: 36px;
        font-weight: 700;
        margin: 8px 0 4px 0;
        line-height: 1;
    }
    
    .metric-label {
        color: #64748B;
        font-size: 12px;
        font-weight: 400;
        margin: 0;
    }
    
    /* Chart containers */
    .chart-container {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
    }
    
    .chart-title {
        color: #F8FAFC;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    /* Header styling */
    .dashboard-header {
        color: #F8FAFC;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 32px;
        padding: 0;
    }
    
    /* Navigation */
    .nav-item {
        color: #CBD5E1;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 8px;
        text-decoration: none;
    }
    
    .nav-item:hover {
        background-color: #334155;
        color: #F8FAFC;
    }
    
    .nav-item.active {
        background-color: #5865F2;
        color: #FFFFFF;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #1E293B;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 0; text-align: center;">
        <h2 style="color: #F8FAFC; margin: 0; font-weight: 700;">HR<span style="color: #5865F2;">RemotelyX</span></h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    nav_options = ["📊 Dashboard", "📅 Calendar", "👥 Candidates", "👨‍💼 Employees", "📄 Documents"]
    page = st.radio("", nav_options, index=0)
    
    st.markdown("---")
    
    # Filters section
    st.markdown("### Filters")
    
    # Date filter
    date_range = st.date_input(
        "Date Range",
        value=[datetime.now() - timedelta(days=30), datetime.now()],
        max_value=datetime.now()
    )
    
    # Department filter
    if not jobs_df.empty and 'department' in jobs_df.columns:
        departments = st.multiselect(
            "Departments",
            options=jobs_df['department'].unique(),
            default=jobs_df['department'].unique()
        )
    else:
        departments = []

# Main dashboard
if page == "📊 Dashboard":
    st.markdown('<h1 class="dashboard-header">Data Insight</h1>', unsafe_allow_html=True)
    
    # Filter data based on selections
    if not jobs_df.empty and departments:
        filtered_jobs = jobs_df[jobs_df['department'].isin(departments)]
        if not applications_df.empty:
            filtered_applications = applications_df[
                applications_df['job_id'].isin(filtered_jobs['job_id'])
            ]
        else:
            filtered_applications = pd.DataFrame()
    else:
        filtered_jobs = jobs_df
        filtered_applications = applications_df
    
    # Row 1: Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_jobs = len(filtered_jobs) if not filtered_jobs.empty else 124
        st.markdown(f"""
        <div class="metric-card metric-blue">
            <div>
                <div class="metric-icon">📊</div>
                <p class="metric-title">Total Jobs</p>
            </div>
            <div>
                <h1 class="metric-value">{total_jobs}</h1>
                <p class="metric-label">jobs</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        top_skills_count = len(skills_df) if not skills_df.empty else 45
        st.markdown(f"""
        <div class="metric-card metric-red">
            <div>
                <div class="metric-icon">📈</div>
                <p class="metric-title">Top Skills</p>
            </div>
            <div>
                <h1 class="metric-value">{top_skills_count}</h1>
                <p class="metric-label">skills</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        top_roles_count = len(filtered_jobs['title'].unique()) if not filtered_jobs.empty else 75
        st.markdown(f"""
        <div class="metric-card metric-yellow">
            <div>
                <div class="metric-icon">👤</div>
                <p class="metric-title">Top Roles</p>
            </div>
            <div>
                <h1 class="metric-value">{top_roles_count}</h1>
                <p class="metric-label">roles</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_applications = len(filtered_applications) if not filtered_applications.empty else 115
        st.markdown(f"""
        <div class="metric-card metric-teal">
            <div>
                <div class="metric-icon">📋</div>
                <p class="metric-title">Total Applications</p>
            </div>
            <div>
                <h1 class="metric-value">{total_applications}</h1>
                <p class="metric-label">applications</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Row 2: Pipeline & Hiring
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">Application Funnel</h3>
        """, unsafe_allow_html=True)
        
        # Application funnel data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        
        fig_funnel = go.Figure()
        
        # Create stacked bar chart for application funnel
        stages = ['Applied', 'Interviewed', 'Rejected', 'Hired']
        colors_funnel = [COLORS['primary_blue'], COLORS['yellow'], COLORS['red'], COLORS['light_teal']]
        
        for i, stage in enumerate(stages):
            values = np.random.randint(10, 50, len(months))
            fig_funnel.add_trace(go.Bar(
                name=stage,
                x=months,
                y=values,
                marker_color=colors_funnel[i],
                marker_line=dict(width=0)
            ))
        
        fig_funnel.update_layout(
            barmode='stack',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#CBD5E1', family='Inter'),
            height=280,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(
                showgrid=False,
                showline=False,
                zeroline=False,
                color='#CBD5E1'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(203, 213, 225, 0.1)',
                showline=False,
                zeroline=False,
                color='#CBD5E1'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font=dict(color='#CBD5E1')
            )
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">Salary Range</h3>
        """, unsafe_allow_html=True)
        
        # Salary range distribution
        if not filtered_jobs.empty and 'salary_range' in filtered_jobs.columns:
            salary_counts = filtered_jobs['salary_range'].value_counts()
        else:
            salary_counts = pd.Series([25, 35, 30, 20, 15], 
                                    index=['$60k-$80k', '$80k-$100k', '$100k-$120k', '$120k-$150k', '$150k+'])
        
        fig_salary = go.Figure(data=[
            go.Bar(
                x=salary_counts.index,
                y=salary_counts.values,
                marker_color=[COLORS['primary_blue'], COLORS['secondary_purple'], COLORS['light_teal'], 
                             COLORS['yellow'], COLORS['red']],
                marker_line=dict(width=0)
            )
        ])
        
        fig_salary.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#CBD5E1', family='Inter'),
            height=280,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                showline=False,
                zeroline=False,
                color='#CBD5E1'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(203, 213, 225, 0.1)',
                showline=False,
                zeroline=False,
                color='#CBD5E1'
            )
        )
        
        st.plotly_chart(fig_salary, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Row 3: Trends & Activity
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">Current Activity</h3>
        """, unsafe_allow_html=True)
        
        # Job postings over time
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        job_postings = np.random.poisson(8, len(dates)) + np.sin(np.arange(len(dates)) * 0.2) * 3 + 5
        previous_postings = np.random.poisson(6, len(dates)) + np.sin(np.arange(len(dates)) * 0.15) * 2 + 3
        
        fig_activity = go.Figure()
        
        fig_activity.add_trace(go.Scatter(
            x=dates,
            y=job_postings,
            mode='lines',
            name='Job Postings',
            line=dict(color=COLORS['primary_blue'], width=3),
            fill='tonexty',
            fillcolor=f'rgba(88, 101, 242, 0.1)'
        ))
        
        fig_activity.add_trace(go.Scatter(
            x=dates,
            y=previous_postings,
            mode='lines',
            name='Previous Period',
            line=dict(color=COLORS['secondary_purple'], width=2),
            fill='tozeroy',
            fillcolor=f'rgba(124, 58, 237, 0.1)'
        ))
        
        fig_activity.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#CBD5E1', family='Inter'),
            height=280,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(
                showgrid=False,
                showline=False,
                zeroline=False,
                color='#CBD5E1'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(203, 213, 225, 0.1)',
                showline=False,
                zeroline=False,
                color='#CBD5E1',
                title='Number of Job Postings'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font=dict(color='#CBD5E1')
            )
        )
        
        st.plotly_chart(fig_activity, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-container">
            <h3 class="chart-title">Jobs Distribution</h3>
        """, unsafe_allow_html=True)
        
        # Location distribution pie chart
        st.markdown('<p style="color: #CBD5E1; font-weight: 600; margin: 20px 0 10px 0;">Per Location</p>', unsafe_allow_html=True)
        
        if not filtered_jobs.empty and 'location' in filtered_jobs.columns:
            location_counts = filtered_jobs['location'].value_counts()
        else:
            location_counts = pd.Series([30, 25, 20, 15, 10], 
                                      index=['Remote', 'New York', 'San Francisco', 'London', 'Berlin'])
        
        fig_location = go.Figure(data=[go.Pie(
            labels=location_counts.index,
            values=location_counts.values,
            hole=0.6,
            marker_colors=[COLORS['red'], COLORS['yellow'], COLORS['light_teal'], 
                          COLORS['primary_blue'], COLORS['coral']],
            textinfo='none',
            showlegend=False
        )])
        
        fig_location.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#CBD5E1', family='Inter'),
            height=150,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig_location, use_container_width=True)
        
        # Seniority distribution pie chart
        st.markdown('<p style="color: #CBD5E1; font-weight: 600; margin: 20px 0 10px 0;">Per Seniority</p>', unsafe_allow_html=True)
        
        if not filtered_jobs.empty and 'seniority' in filtered_jobs.columns:
            seniority_counts = filtered_jobs['seniority'].value_counts()
        else:
            seniority_counts = pd.Series([45, 40, 35], index=['Mid', 'Senior', 'Junior'])
        
        fig_seniority = go.Figure(data=[go.Pie(
            labels=seniority_counts.index,
            values=seniority_counts.values,
            hole=0.6,
            marker_colors=[COLORS['primary_blue'], COLORS['red'], COLORS['yellow']],
            textinfo='none',
            showlegend=False
        )])
        
        fig_seniority.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#CBD5E1', family='Inter'),
            height=150,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig_seniority, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Other pages (placeholder content)
elif page == "📅 Calendar":
    st.markdown('<h1 class="dashboard-header">Calendar</h1>', unsafe_allow_html=True)
    st.info("Calendar functionality would be implemented here")

elif page == "👥 Candidates":
    st.markdown('<h1 class="dashboard-header">Candidates</h1>', unsafe_allow_html=True)
    if not applications_df.empty and not jobs_df.empty:
        candidate_data = applications_df.merge(jobs_df, on='job_id')[['candidate_name', 'title', 'department', 'stage', 'application_date']]
        st.dataframe(candidate_data, use_container_width=True)
    else:
        st.info("No candidate data available")

elif page == "👨‍💼 Employees":
    st.markdown('<h1 class="dashboard-header">Employees</h1>', unsafe_allow_html=True)
    st.info("Employee management functionality would be implemented here")

elif page == "📄 Documents":
    st.markdown('<h1 class="dashboard-header">Documents</h1>', unsafe_allow_html=True)
    st.info("Document management functionality would be implemented here")