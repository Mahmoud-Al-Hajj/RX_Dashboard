# Quick Setup Guide for RemotelyX Job Automation

## 🚀 Getting Started

### 1. Configure Environment Variables

Edit the `.env` file with your credentials:

```env
# Gmail Configuration (REQUIRED)
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
SENDER_EMAIL=jobs@remotelyx.com

# MongoDB Configuration (OPTIONAL - defaults to localhost)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=remotelyx_jobs
MONGODB_COLLECTION=job_postings

# Other settings (OPTIONAL - have good defaults)
SUBJECT_KEYWORD=RemotelyX
EXCEL_FILE_PATH=./data/remotelyx_jobs.xlsx
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
LOG_FILE=./logs/remotelyx.log
```

### 2. Gmail Setup (Required)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Use the generated password** in `GMAIL_PASSWORD`

### 3. MongoDB Setup (Choose one option)

#### Option A: Local MongoDB
```bash
# Install MongoDB locally or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:6.0
```

#### Option B: MongoDB Atlas (Cloud)
- Create free account at https://www.mongodb.com/atlas
- Get connection string and update `MONGODB_URI`

#### Option C: Use Docker Compose (Recommended)
```bash
docker-compose up -d mongodb
```

## 🏃‍♂️ Running the Service

### Option 1: API Server Mode
```bash
python main.py api
```
- Access API at: http://localhost:8000
- API docs at: http://localhost:8000/docs

### Option 2: Scheduled Mode
```bash
python main.py scheduler --interval 30 --email-limit 10
```

### Option 3: One-time Processing
```bash
python main.py process
```

### Option 4: Test Mode
```bash
python main.py test
```

### Option 5: Docker (Full Stack)
```bash
# Start everything with Docker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔧 Testing Your Setup

Run the test script to verify everything works:
```bash
python test_setup.py
```

## 📊 API Endpoints

Once running, you can:

- **POST** `/workflow/run` - Run job processing
- **GET** `/jobs` - Get all job postings
- **GET** `/statistics` - Get processing stats
- **POST** `/excel/export` - Export to Excel
- **GET** `/health` - Health check

## 🐛 Troubleshooting

### Common Issues:

1. **Gmail Connection Failed**
   - Verify 2FA is enabled
   - Use App Password, not regular password
   - Check if IMAP is enabled

2. **MongoDB Connection Failed**
   - Ensure MongoDB is running
   - Check connection string
   - Try Docker: `docker run -d -p 27017:27017 mongo:6.0`

3. **Missing Dependencies**
   - Run: `pip install -r requirements.txt`

4. **Permission Errors**
   - Ensure you have write access to the project directory

## 📁 File Structure

```
RemotelyX Dashboard/
├── .env                    # Your configuration (create from env.example)
├── main.py                 # Main entry point
├── api.py                  # FastAPI server
├── job_processor.py        # Core workflow
├── email_service.py        # Gmail integration
├── scraper.py              # Web scraping
├── database.py             # MongoDB operations
├── excel_exporter.py       # Excel export
├── config.py               # Configuration
├── models.py               # Data models
├── scheduler.py            # Automated processing
├── data/                   # Excel files (auto-created)
├── logs/                   # Log files (auto-created)
└── requirements.txt        # Python dependencies
```

## 🎯 Next Steps

1. Configure your `.env` file with Gmail credentials
2. Start MongoDB (local or cloud)
3. Run: `python main.py api`
4. Visit: http://localhost:8000/docs
5. Test the workflow endpoint

## 📞 Support

If you encounter issues:
1. Check the logs in `./logs/remotelyx.log`
2. Run `python main.py test` for diagnostics
3. Ensure all environment variables are set correctly 