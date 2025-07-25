#!/usr/bin/env python3
"""
Test script for the Production Demo environment
This script tests the dummy data generation and API endpoints
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_sage_scraping():
    """Test Sage dummy data generation"""
    print("\n🔍 Testing Sage dummy data generation...")
    try:
        response = requests.post(f"{BASE_URL}/api/scrape/test-sage")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sage scraping successful:")
            print(f"   - Total reviews: {data.get('totalReviews', 0)}")
            print(f"   - Average sentiment: {data.get('averageSentiment', 0):.3f}")
            print(f"   - Average rating: {data.get('averageRating', 0):.1f}")
            print(f"   - Stored in Supabase: {data.get('storedInSupabase', False)}")
            return True
        else:
            print(f"❌ Sage scraping failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sage scraping error: {e}")
        return False

def test_live_scraping():
    """Test live scraping with multiple companies"""
    print("\n🔍 Testing live scraping with multiple companies...")
    try:
        payload = {
            "companies": ["Sage", "QuickBooks"]
        }
        response = requests.post(f"{BASE_URL}/api/scrape/live", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Live scraping successful:")
            print(f"   - Total reviews: {data.get('totalReviews', 0)}")
            print(f"   - Companies processed: {data.get('companiesProcessed', 0)}")
            print(f"   - Average sentiment: {data.get('averageSentiment', 0):.3f}")
            print(f"   - Stored in Supabase: {data.get('storedInSupabase', False)}")
            print(f"   - Processing time: {data.get('processingTime', '0s')}")
            return True
        else:
            print(f"❌ Live scraping failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Live scraping error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Production Demo Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Sage Scraping", test_sage_scraping),
        ("Live Scraping", test_live_scraping)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Production demo is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the server and try again.")
    
    print("\n💡 To start the production demo server:")
    print("   python backend/integrated_review_scraper_production.py")
    print("   or")
    print("   .\\start-production-demo.bat")

if __name__ == "__main__":
    main() 