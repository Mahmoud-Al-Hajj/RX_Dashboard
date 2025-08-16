# 🚀 RemotelyX Job Automation Dashboard

A complete workflow and dashboard system for extracting, storing, and presenting skills needed for jobs in the US. The system automatically processes job descriptions from RemotelyX emails and provides comprehensive analytics.

## ✨ Features

- **🔍 Intelligent Web Scraping**: Automatically extracts job details from RemotelyX job pages
- **🗄️ MongoDB Storage**: Non-relational database for flexible job data storage
- **📊 Interactive Dashboard**: Beautiful Streamlit dashboard with real-time analytics
- **📈 Excel Export**: Export job data to Excel with backup functionality
- **🔄 REST API**: FastAPI backend for integration with n8n workflows
- **🤖 Automation Ready**: Designed to work with n8n for email-triggered workflows

## 🏗️ Architecture

```
Gmail Trigger (n8n)
    ↓
Extract Job Links (n8n Function)
    ↓
HTTP Request to API (n8n)
    ↓
Scrape & Process Jobs (Python)
    ↓
Store in MongoDB
    ↓
Update Dashboard
    ↓
Export to Excel
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Git

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd RemotelyX-Dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy environment template
copy env.example .env

# Edit .env with your settings
# MongoDB connection, API keys, etc.
```

### 4. Start MongoDB

```bash
# Windows
mongod

# macOS/Linux
sudo systemctl start mongod
```

### 5. Test the System

```bash
# Run system tests
python test_system.py

# Or use the Windows batch file
start.bat
```

## 🎯 Usage

### Start API Server

```bash
python main.py api
```

API will be available at: http://localhost:8000
Documentation: http://localhost:8000/docs

### Start Dashboard

```bash
python main.py dashboard
```

Dashboard will be available at: http://localhost:8501

### Run Workflow Manually

```bash
python main.py workflow --urls "https://remotelyx.com/job/123" "https://remotelyx.com/job/456"
```

### Export to Excel

```bash
python main.py export
```

### View Statistics

```bash
python main.py stats
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `remotelyx_jobs` |
| `MONGODB_COLLECTION` | Collection name | `job_postings` |
| `EXCEL_FILE_PATH` | Excel export path | `data/job_postings.xlsx` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `HOST` | API server host | `0.0.0.0` |
| `PORT` | API server port | `8000` |

### MongoDB Setup

1. Install MongoDB Community Edition
2. Start MongoDB service
3. Create database (optional - will be created automatically)
4. Update connection string in `.env`

## 📊 Dashboard Features

- **Real-time Analytics**: Job counts, company breakdowns, location analysis
- **Interactive Charts**: Plotly-powered visualizations
- **Job Management**: View, filter, and manage job postings
- **Export Controls**: Excel export and backup management
- **Health Monitoring**: System status and API connectivity

## 🔌 API Endpoints

### Core Endpoints

- `GET /health` - System health check
- `GET /jobs` - List job postings
- `POST /jobs` - Create new job posting
- `GET /jobs/{id}` - Get specific job
- `PUT /jobs/{id}` - Update job posting
- `DELETE /jobs/{id}` - Delete job posting

### Workflow Endpoints

- `POST /workflow/run` - Run complete workflow
- `POST /workflow/scrape` - Scrape job URLs
- `POST /workflow/enrich` - Enrich job data

### Analytics Endpoints

- `GET /statistics` - Comprehensive statistics
- `GET /companies` - List all companies
- `GET /locations` - List all locations
- `GET /skills` - List all skills

### Export Endpoints

- `POST /excel/export` - Export to Excel
- `POST /excel/backup` - Create backup
- `GET /excel/backups` - List backups

## 🤖 n8n Integration

### Workflow Setup

1. **Gmail Trigger**: Monitor for emails with "RemotelyX" in subject
2. **Extract Links**: Use Function node to extract job URLs from email body
3. **HTTP Request**: Send job URLs to `/workflow/run` endpoint
4. **Monitor Progress**: Check workflow status via API
5. **Export Results**: Use `/excel/export` endpoint for final data

### Sample n8n Function

```javascript
// Extract job URLs from email body
const emailBody = $input.all()[0].json.body;
const urlRegex = /https?:\/\/[^\s]+/g;
const urls = emailBody.match(urlRegex);

// Filter for RemotelyX URLs
const remotelyxUrls = urls.filter(url => 
  url.includes('remotelyx.com') || url.includes('remotelyx')
);

return { urls: remotelyxUrls };
```

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t remotelyx-dashboard .
```

### Run Container

```bash
docker run -d \
  --name remotelyx-dashboard \
  -p 8000:8000 \
  -p 8501:8501 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017 \
  remotelyx-dashboard
```

### Docker Compose

```bash
docker-compose up -d
```

## ☁️ AWS Deployment

### EC2 Setup

1. Launch EC2 instance (t3.medium recommended)
2. Install Docker and Docker Compose
3. Clone repository
4. Configure environment variables
5. Run with Docker Compose

### Environment Variables for Production

```bash
DEBUG=false
LOG_LEVEL=WARNING
MONGODB_URI=mongodb://your-mongodb-uri
HOST=0.0.0.0
PORT=8000
```

## 🧪 Testing

### Run Tests

```bash
# System test
python test_system.py

# API tests (if implemented)
pytest tests/
```

### Test Workflow

```bash
# Test with sample URLs
python main.py workflow --urls "https://example.com/job1" "https://example.com/job2"
```

## 📁 Project Structure

```
RemotelyX-Dashboard/
├── src/
│   ├── api/           # FastAPI backend
│   ├── core/          # Configuration & database
│   ├── dashboard/     # Streamlit dashboard
│   ├── models/        # Data models
│   ├── services/      # Business logic
│   └── utils/         # Utilities
├── data/              # Excel files & backups
├── logs/              # Application logs
├── main.py            # Main entry point
├── test_system.py     # System test script
├── start.bat          # Windows startup script
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
└── README.md          # This file
```

## 🔍 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Ensure MongoDB is running
   - Check connection string in `.env`
   - Verify network connectivity

2. **Import Errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **Dashboard Not Loading**
   - Check if API server is running
   - Verify ports (8000 for API, 8501 for dashboard)
   - Check browser console for errors

4. **Scraping Failures**
   - Check internet connectivity
   - Verify target URLs are accessible
   - Check rate limiting settings

### Logs

- Application logs: `logs/app.log`
- API logs: Check console output
- Dashboard logs: Check Streamlit output

**Built with ❤️ for the RemotelyX community** 
