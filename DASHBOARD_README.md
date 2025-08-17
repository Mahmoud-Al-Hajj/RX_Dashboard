# HR RemotelyX Dashboard

A modern, dark-themed HR dashboard built with Streamlit and MongoDB integration for comprehensive job analytics and management.

## 🎨 Design Features

- **Dark Theme**: Professional dark UI with blue accent colors
- **Modern Layout**: Clean, responsive design matching Figma specifications
- **Three Main Sections**: 
  - Quick Check (Data Insights)
  - Pipeline & Who's Hiring
  - Trends & Detailed Activity

## 📊 Dashboard Sections

### 1. Quick Check (Data Insights)
- **Total Jobs**: Overview of all job postings
- **Top Skills**: Most requested skills across jobs
- **Top Roles**: Seniority level distribution
- **Total Applications**: Application tracking metrics

### 2. Pipeline & Who's Hiring
- **Application Funnel**: Visual representation of application stages
- **Salary Range Distribution**: Job distribution by salary brackets
- **Companies Hiring**: Active companies and their job counts

### 3. Trends & Detailed Activity
- **Current Activity**: Job posting timeline over time
- **Jobs Distribution**: Location and seniority breakdowns
- **Recent Job Postings**: Latest job listings

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MongoDB
- Required Python packages (see requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RX_Dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your MongoDB connection details
   ```

4. **Start the API server**
   ```bash
   python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Start the dashboard**
   ```bash
   streamlit run src/dashboard/main.py
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the dashboard**
   - Dashboard: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## 🔧 API Endpoints

### Dashboard Analytics
- `GET /dashboard/analytics` - Comprehensive dashboard data
- `GET /dashboard/quick-check` - Quick metrics
- `GET /dashboard/pipeline` - Pipeline and hiring data
- `GET /dashboard/trends` - Trends and activity data

### Job Management
- `GET /jobs` - List jobs with filters
- `POST /jobs` - Create new job
- `PUT /jobs/{id}` - Update job
- `DELETE /jobs/{id}` - Delete job

### Statistics
- `GET /statistics` - General statistics
- `GET /companies` - List companies
- `GET /locations` - List locations
- `GET /skills` - List skills

## 📈 MongoDB Queries

The dashboard uses optimized MongoDB queries for:

### Quick Check Metrics
```javascript
// Total jobs count
db.jobs.countDocuments({})

// Skills frequency
db.jobs.aggregate([
  { $unwind: "$skills" },
  { $group: { _id: "$skills", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 50 }
])

// Seniority distribution
db.jobs.aggregate([
  { $group: { _id: "$seniority_level", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Pipeline Data
```javascript
// Companies hiring
db.jobs.aggregate([
  { $group: { _id: "$company", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
])

// Salary range analysis
db.jobs.aggregate([
  { $match: { salary_min: { $exists: true } } },
  { $group: { _id: "$salary_range", count: { $sum: 1 } } }
])
```

### Trends Analysis
```javascript
// Job activity timeline
db.jobs.aggregate([
  { $group: { 
    _id: { 
      $dateToString: { format: "%Y-%m-%d", date: "$posting_date" } 
    }, 
    count: { $sum: 1 } 
  }},
  { $sort: { _id: 1 } }
])

// Location distribution
db.jobs.aggregate([
  { $group: { _id: "$location", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 5 }
])
```

## 🎨 Customization

### Colors
The dashboard uses a consistent color palette:
- Primary Blue: `#4a90e2`
- Orange: `#ff6b35`
- Yellow: `#ffd93d`
- Green: `#4caf50`
- Red: `#e74c3c`
- Background: `#1a1a1a`
- Card Background: `#2d2d2d`

### Styling
Custom CSS is applied for:
- Dark theme backgrounds
- Card styling with gradients
- Navigation highlighting
- Chart theming

## 🔍 Testing

Run the test script to verify functionality:
```bash
python test_dashboard.py
```

This will test:
- API connectivity
- Dashboard endpoints
- Basic functionality

## 📝 Features

### Real-time Data
- Live MongoDB queries
- Real-time statistics updates
- Dynamic chart generation

### Interactive Elements
- Time period selectors
- Filterable data
- Responsive charts
- Search functionality

### Data Visualization
- Application funnel charts
- Salary distribution bars
- Activity timeline graphs
- Location/seniority pie charts

## 🛠️ Development

### Adding New Charts
1. Create chart function in `src/dashboard/main.py`
2. Add corresponding API endpoint in `src/api/main.py`
3. Update dashboard layout to include new chart

### Adding New Metrics
1. Extend the analytics endpoints
2. Update the quick check section
3. Add corresponding MongoDB queries

### Styling Changes
- Modify CSS in the dashboard file
- Update color variables
- Adjust layout components

## 📊 Data Sources

The dashboard pulls data from:
- **Job Postings**: Scraped and processed job data
- **Company Information**: Employer details and activity
- **Skills Analysis**: Extracted and categorized skills
- **Salary Data**: Parsed compensation information
- **Location Data**: Geographic distribution analysis

## 🔐 Security

- API authentication (to be implemented)
- Input validation
- SQL injection prevention
- CORS configuration

## 📈 Performance

- Optimized MongoDB queries
- Cached analytics data
- Efficient chart rendering
- Lazy loading for large datasets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with details
4. Contact the development team

---

**Built with ❤️ for HR professionals** 