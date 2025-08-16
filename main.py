#!/usr/bin/env python3
"""
Main entry point for RemotelyX Job Automation Service.
Provides different run modes: API server, dashboard, and command-line tools.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import get_settings
from src.services.job_processor import job_processor


def setup_logging():
    """Setup logging configuration."""
    settings = get_settings()
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler
    logger.add(
        settings.log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days"
    )


async def run_api_server():
    """Run the FastAPI server."""
    import uvicorn
    from src.api.main import app
    
    settings = get_settings()
    
    logger.info("Starting RemotelyX Job Automation API Server")
    logger.info(f"Server will be available at: http://{settings.host}:{settings.port}")
    logger.info(f"API documentation at: http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


def run_dashboard():
    """Run the Streamlit dashboard."""
    import subprocess
    import sys
    
    dashboard_path = Path(__file__).parent / "src" / "dashboard" / "main.py"
    
    logger.info("Starting RemotelyX Job Intel Dashboard")
    logger.info("Dashboard will be available at: http://localhost:8501")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
    except Exception as e:
        logger.error(f"Failed to start dashboard: {e}")


async def run_workflow(job_urls: list):
    """Run the job processing workflow."""
    try:
        logger.info("Initializing job processor...")
        success = await job_processor.initialize()
        if not success:
            logger.error("Failed to initialize job processor")
            return
        
        logger.info(f"Running workflow for {len(job_urls)} job URLs")
        result = await job_processor.run_full_workflow(job_urls)
        
        if result.get("success"):
            logger.success("Workflow completed successfully!")
            logger.info(f"Duration: {result.get('duration', 0):.2f} seconds")
            logger.info(f"Jobs processed: {result.get('scraping', {}).get('jobs_processed', 0)}")
            logger.info(f"Jobs enriched: {result.get('enrichment', {}).get('enriched', 0)}")
        else:
            logger.error("Workflow failed")
            if result.get("error"):
                logger.error(f"Error: {result['error']}")
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
    finally:
        await job_processor.cleanup()


async def run_enrichment(limit: int):
    """Run job enrichment process."""
    try:
        logger.info("Initializing job processor...")
        success = await job_processor.initialize()
        if not success:
            logger.error("Failed to initialize job processor")
            return
        
        logger.info(f"Running job enrichment (limit: {limit})")
        result = await job_processor.enrich_jobs(limit=limit)
        
        logger.info(f"Enrichment completed: {result.get('enriched', 0)} jobs enriched")
        
    except Exception as e:
        logger.error(f"Enrichment failed: {e}")
    finally:
        await job_processor.cleanup()


async def run_export():
    """Run Excel export."""
    try:
        logger.info("Initializing job processor...")
        success = await job_processor.initialize()
        if not success:
            logger.error("Failed to initialize job processor")
            return
        
        logger.info("Running Excel export...")
        result = await job_processor.export_to_excel()
        
        if result.get("success"):
            logger.success(f"Excel export completed: {result.get('exported', 0)} jobs exported")
            logger.info(f"File saved to: {result.get('file_path', 'Unknown')}")
        else:
            logger.error("Excel export failed")
            if result.get("error"):
                logger.error(f"Error: {result['error']}")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
    finally:
        await job_processor.cleanup()


async def run_statistics():
    """Display system statistics."""
    try:
        logger.info("Initializing job processor...")
        success = await job_processor.initialize()
        if not success:
            logger.error("Failed to initialize job processor")
            return
        
        logger.info("Fetching statistics...")
        stats = await job_processor.get_statistics()
        
        if "database" in stats:
            db_stats = stats["database"]
            logger.info("=== Database Statistics ===")
            logger.info(f"Total Jobs: {db_stats.get('total_jobs', 0)}")
            logger.info(f"Processed Jobs: {db_stats.get('processed_jobs', 0)}")
            logger.info(f"Enriched Jobs: {db_stats.get('enriched_jobs', 0)}")
            logger.info(f"Companies: {len(db_stats.get('by_company', {}))}")
            logger.info(f"Locations: {len(db_stats.get('by_location', {}))}")
        
        if "excel" in stats:
            excel_stats = stats["excel"]
            if excel_stats:
                logger.info("=== Excel Statistics ===")
                logger.info(f"Total Rows: {excel_stats.get('total_rows', 0)}")
                logger.info(f"File Size: {excel_stats.get('file_size_mb', 0)} MB")
                logger.info(f"Last Modified: {excel_stats.get('last_modified', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
    finally:
        await job_processor.cleanup()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RemotelyX Job Automation Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py api                    # Start API server
  python main.py dashboard              # Start Streamlit dashboard
  python main.py workflow --urls url1 url2  # Run workflow with job URLs
  python main.py enrich --limit 100     # Enrich jobs
  python main.py export                 # Export to Excel
  python main.py stats                  # Show statistics
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # API server command
    subparsers.add_parser("api", help="Start the FastAPI server")
    
    # Dashboard command
    subparsers.add_parser("dashboard", help="Start the Streamlit dashboard")
    
    # Workflow command
    workflow_parser = subparsers.add_parser("workflow", help="Run job processing workflow")
    workflow_parser.add_argument("--urls", nargs="+", required=True, help="Job URLs to process")
    
    # Enrichment command
    enrich_parser = subparsers.add_parser("enrich", help="Enrich job postings")
    enrich_parser.add_argument("--limit", type=int, default=100, help="Maximum jobs to enrich")
    
    # Export command
    subparsers.add_parser("export", help="Export jobs to Excel")
    
    # Statistics command
    subparsers.add_parser("stats", help="Show system statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Setup logging
    setup_logging()
    
    # Ensure directories exist
    settings = get_settings()
    settings.ensure_directories()
    
    logger.info("🚀 RemotelyX Job Automation Service")
    logger.info(f"Version: {settings.app_version}")
    logger.info(f"Debug Mode: {settings.debug}")
    
    try:
        if args.command == "api":
            asyncio.run(run_api_server())
        elif args.command == "dashboard":
            run_dashboard()
        elif args.command == "workflow":
            asyncio.run(run_workflow(args.urls))
        elif args.command == "enrich":
            asyncio.run(run_enrichment(args.limit))
        elif args.command == "export":
            asyncio.run(run_export())
        elif args.command == "stats":
            asyncio.run(run_statistics())
        else:
            logger.error(f"Unknown command: {args.command}")
            parser.print_help()
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 