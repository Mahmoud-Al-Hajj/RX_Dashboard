#!/usr/bin/env python3
"""
Test script for the RemotelyX HR Dashboard
Tests API endpoints and dashboard functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"  # Adjust if needed

def test_api_health():
    """Test API health endpoint"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy")
            print(f"   Status: {response.json()}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_dashboard_endpoints():
    """Test dashboard-specific endpoints"""
    print("\n📊 Testing dashboard endpoints...")
    
    endpoints = [
        "/dashboard/quick-check",
        "/dashboard/pipeline", 
        "/dashboard/trends",
        "/dashboard/analytics"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"   Testing {endpoint}...")
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {endpoint} - OK")
                print(f"      Data keys: {list(data.keys())}")
            else:
                print(f"   ❌ {endpoint} - Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")

def test_basic_endpoints():
    """Test basic API endpoints"""
    print("\n🔧 Testing basic endpoints...")
    
    endpoints = [
        "/jobs?limit=5",
        "/statistics",
        "/companies",
        "/locations",
        "/skills"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"   Testing {endpoint}...")
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {endpoint} - OK")
                if isinstance(data, list):
                    print(f"      Items: {len(data)}")
                elif isinstance(data, dict):
                    print(f"      Keys: {list(data.keys())}")
            else:
                print(f"   ❌ {endpoint} - Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")

def main():
    """Main test function"""
    print("🚀 RemotelyX HR Dashboard Test")
    print("=" * 40)
    print(f"API URL: {API_BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API health first
    if not test_api_health():
        print("\n❌ API is not available. Please start the API server first.")
        print("   Run: python -m uvicorn src.api.main:app --reload")
        return
    
    # Test basic endpoints
    test_basic_endpoints()
    
    # Test dashboard endpoints
    test_dashboard_endpoints()
    
    print("\n✅ Test completed!")
    print("\n📝 To start the dashboard:")
    print("   streamlit run src/dashboard/main.py")

if __name__ == "__main__":
    main() 