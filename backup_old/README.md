# RemotelyX Job Automation Backend

A production-ready Python backend service for automating RemotelyX job description processing. This service monitors Gmail for new job emails, scrapes job details from web pages, stores data in MongoDB, and exports to Excel files.

## Features

- **Email Monitoring**: Connects to Gmail/IMAP to detect new emails from specific senders
- **Web Scraping**: Extracts job details (title, skills, location, company, salary) from job posting pages
- **Database Storage**: MongoDB integration with clean schema and indexing
- **Excel Export**: Automatic export to Excel files with formatting
- **REST API**: FastAPI-based API for integration with n8n workflows
- **Scheduled Processing**: Automated job processing with configurable intervals
- **Error Handling**: Comprehensive error handling and logging
- **Modular Architecture**: Clean separation of concerns with reusable components

## Architecture

```
├── config.py          # Configuration and environment variables
├── models.py          # Pydantic data models
├── database.py        # MongoDB connection and operations
├── email_service.py   # Gmail/IMAP email processing
├── scraper.py         # Web scraping for job details
├── excel_exporter.py  # Excel file export functionality
├── job_processor.py   # Main workflow orchestration
├── api.py            # FastAPI REST endpoints
├── scheduler.py      # Automated job processing scheduler
└── main.py           # Application entry point
```

## Prerequisites

- Python 3.8+
- MongoDB (local or cloud)
- Gmail account with IMAP access
- Gmail App Password (for 2FA accounts)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd remotelyx-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Gmail Configuration
   GMAIL_EMAIL=your-email@gmail.com
   GMAIL_PASSWORD=your-app-password
   SENDER_EMAIL=jobs@remotelyx.com
   
   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DATABASE=remotelyx_jobs
   
   # Other settings...
   ```

4. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Create database and collection (auto-created on first run)

## Usage

### 1. API Server Mode

Run the service as a REST API server:

```bash
python main.py api
```

The API will be available at `http://localhost:8000` with automatic documentation at `/docs`.

### 2. Scheduled Service Mode

Run automated job processing at regular intervals:

```bash
python main.py scheduler --interval 30 --email-limit 10
```

### 3. One-time Processing

Run job processing once:

```bash
python main.py process
```

### 4. Test Mode

Test all components:

```bash
python main.py test
```

## API Endpoints

### Core Workflow

- `POST /workflow/run` - Run the complete job processing workflow
- `GET /jobs` - Get all job postings
- `GET /jobs/{job_id}` - Get specific job posting
- `GET /statistics` - Get processing statistics

### Excel Operations

- `POST /excel/export` - Export unprocessed jobs to Excel
- `POST /excel/backup` - Create Excel file backup
- `GET /excel/statistics` - Get Excel file statistics

### System

- `GET /` - Root endpoint
- `GET /health` - Health check
- `DELETE /jobs/{job_id}` - Delete job posting

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GMAIL_EMAIL` | Gmail account email | Required |
| `GMAIL_PASSWORD` | Gmail app password | Required |
| `SENDER_EMAIL` | Email sender to monitor | Required |
| `SUBJECT_KEYWORD` | Subject keyword filter | "RemotelyX" |
| `MONGODB_URI` | MongoDB connection string | "mongodb://localhost:27017" |
| `MONGODB_DATABASE` | MongoDB database name | "remotelyx_jobs" |
| `EXCEL_FILE_PATH` | Excel file path | "./data/remotelyx_jobs.xlsx" |
| `API_HOST` | API server host | "0.0.0.0" |
| `API_PORT` | API server port | 8000 |

### Gmail Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use the generated password in `GMAIL_PASSWORD`

## Data Models

### JobPosting

```python
{
    "id": "ObjectId",
    "job_title": "string",
    "company": "string", 
    "location": "string",
    "skills": ["string"],
    "salary": "string (optional)",
    "job_url": "string",
    "email_subject": "string",
    "email_date": "datetime",
    "scraped_at": "datetime",
    "processed": "boolean"
}
```

## Integration with n8n

### Webhook Integration

1. **Trigger Workflow**: Use the `/workflow/run` endpoint as a webhook trigger
2. **Get Jobs**: Use `/jobs` endpoint to retrieve processed jobs
3. **Monitor Health**: Use `/health` endpoint for monitoring

### Example n8n Workflow

```json
{
  "nodes": [
    {
      "type": "webhook",
      "url": "http://localhost:8000/workflow/run",
      "method": "POST"
    },
    {
      "type": "httpRequest",
      "url": "http://localhost:8000/jobs",
      "method": "GET"
    },
    {
      "type": "excel",
      "operation": "append",
      "file": "remotelyx_jobs.xlsx"
    }
  ]
}
```

## Error Handling

The service includes comprehensive error handling:

- **Connection Retries**: Automatic retry for network operations
- **Graceful Degradation**: Continues processing even if some components fail
- **Detailed Logging**: All operations are logged with appropriate levels
- **Health Checks**: Built-in health monitoring endpoints

## Logging

Logs are written to both console and file (`./logs/remotelyx.log`):

```bash
# View logs
tail -f logs/remotelyx.log

# Filter by level
grep "ERROR" logs/remotelyx.log
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Statistics

```bash
curl http://localhost:8000/statistics
```

## Troubleshooting

### Common Issues

1. **Gmail Connection Failed**
   - Verify Gmail credentials
   - Check if 2FA is enabled and app password is used
   - Ensure IMAP is enabled in Gmail settings

2. **MongoDB Connection Failed**
   - Verify MongoDB is running
   - Check connection string
   - Ensure network access

3. **Web Scraping Failed**
   - Check internet connection
   - Verify job URLs are accessible
   - Some sites may block automated requests

4. **Excel Export Failed**
   - Check file permissions
   - Ensure directory exists
   - Verify file is not locked by another process

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in `.env`.

## Development

### Running Tests

```bash
python main.py test
```

### Code Structure

- **Modular Design**: Each component is self-contained
- **Dependency Injection**: Services are injected where needed
- **Error Boundaries**: Each module handles its own errors
- **Configuration**: Centralized configuration management

### Adding New Features

1. Create new module in appropriate directory
2. Add configuration in `config.py`
3. Update models in `models.py` if needed
4. Add API endpoints in `api.py`
5. Update documentation

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Create an issue with detailed information 