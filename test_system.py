#!/usr/bin/env python3
"""
Simple test script to verify RemotelyX system components are working.
Run this to check if everything is set up correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from src.core.config import get_settings
        print("✅ Config module imported successfully")
        
        from src.core.database import get_database
        print("✅ Database module imported successfully")
        
        from src.models.job_posting import JobPosting, JobPostingCreate
        print("✅ Models imported successfully")
        
        from src.services.scraper import scraper
        print("✅ Scraper imported successfully")
        
        from src.services.job_processor import job_processor
        print("✅ Job processor imported successfully")
        
        from src.services.excel_exporter import excel_exporter
        print("✅ Excel exporter imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n🔍 Testing configuration...")
    
    try:
        from src.core.config import get_settings
        settings = get_settings()
        
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ MongoDB URI: {settings.mongodb_uri}")
        print(f"✅ Database: {settings.mongodb_database}")
        print(f"✅ Excel path: {settings.excel_file_path}")
        
        # Ensure directories exist
        settings.ensure_directories()
        print("✅ Directories created/verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database_connection():
    """Test database connection."""
    print("\n🔍 Testing database connection...")
    
    try:
        import asyncio
        from src.core.database import get_database
        
        async def test_connection():
            db = await get_database()
            connected = await db.connect()
            if connected:
                print("✅ Database connection successful")
                await db.disconnect()
                return True
            else:
                print("❌ Database connection failed")
                return False
        
        result = asyncio.run(test_connection())
        return result
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_scraper():
    """Test scraper functionality."""
    print("\n🔍 Testing scraper...")
    
    try:
        from src.services.scraper import scraper
        
        # Test with a dummy URL (won't actually scrape)
        print("✅ Scraper instance created successfully")
        print(f"✅ User agent: {scraper.settings.user_agent}")
        print(f"✅ Max retries: {scraper.settings.max_retries}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 RemotelyX System Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database Connection", test_database_connection),
        ("Scraper", test_scraper),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to run.")
        print("\nNext steps:")
        print("1. Start MongoDB: mongod")
        print("2. Start API: python main.py api")
        print("3. Start Dashboard: python main.py dashboard")
        print("4. Test workflow: python main.py workflow --urls https://example.com/job1")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("- MongoDB not running (start with: mongod)")
        print("- Missing dependencies (install with: pip install -r requirements.txt)")
        print("- Environment not set up (copy env.example to .env)")

if __name__ == "__main__":
    main() 