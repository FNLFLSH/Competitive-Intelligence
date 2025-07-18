#!/usr/bin/env python3
"""
Test script for Sage and Capterra scraping functionality
"""

import asyncio
import requests
import json
from datetime import datetime

def test_backend_health():
    """Test if the backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_capterra_scraping():
    """Test Capterra scraping for Sage"""
    print("\n🔍 Testing Capterra scraping for Sage...")
    
    try:
        # Test the live scraping endpoint
        payload = {
            "companies": ["Sage"]
        }
        
        response = requests.post(
            "http://localhost:8000/api/scrape/live",
            json=payload,
            timeout=120  # 2 minutes timeout for scraping
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Capterra scraping completed successfully!")
            print(f"📊 Results:")
            print(f"   - Total reviews: {result.get('totalReviews', 0)}")
            print(f"   - Companies processed: {result.get('companiesProcessed', 0)}")
            print(f"   - Processing time: {result.get('processingTime', 'N/A')}")
            print(f"   - Stored in Supabase: {result.get('storedInSupabase', False)}")
            print(f"   - Stored count: {result.get('storedCount', 0)}")
            
            if result.get('companyResults'):
                for company_result in result['companyResults']:
                    print(f"   - {company_result['company']}:")
                    print(f"     * Total reviews: {company_result['totalReviews']}")
                    print(f"     * Average rating: {company_result['averageRating']:.2f}")
                    print(f"     * Average sentiment: {company_result['averageSentiment']:.3f}")
            
            if result.get('errors'):
                print(f"⚠️ Errors encountered:")
                for error in result['errors']:
                    print(f"   - {error}")
            
            return True
        else:
            print(f"❌ Capterra scraping failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_sentiment_analysis():
    """Test sentiment analysis for Sage"""
    print("\n🧠 Testing sentiment analysis for Sage...")
    
    try:
        # Test the live sentiment scraping endpoint
        payload = {
            "companies": ["Sage"]
        }
        
        response = requests.post(
            "http://localhost:8000/api/scrape/live-sentiment",
            json=payload,
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sentiment analysis completed successfully!")
            print(f"📊 Results:")
            print(f"   - Total reviews: {result.get('totalReviews', 0)}")
            print(f"   - Average sentiment: {result.get('averageSentiment', 0):.3f}")
            print(f"   - Processing time: {result.get('processingTime', 'N/A')}")
            
            return True
        else:
            print(f"❌ Sentiment analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_direct_capterra_scraper():
    """Test the direct Capterra scraper function"""
    print("\n🔧 Testing direct Capterra scraper function...")
    
    try:
        # Import the scraper function
        import sys
        import os
        sys.path.append('backend')
        
        from capterra_scraper import scrape_capterra_playwright
        
        # Test with Sage
        async def test_scraper():
            reviews = await scrape_capterra_playwright("Sage", max_reviews=5)
            return reviews
        
        # Run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        reviews = loop.run_until_complete(test_scraper())
        loop.close()
        
        print(f"✅ Direct scraper test completed!")
        print(f"📊 Found {len(reviews)} reviews")
        
        if reviews:
            print("Sample review:")
            sample = reviews[0]
            print(f"   - Reviewer: {sample.get('reviewer_name', 'N/A')}")
            print(f"   - Rating: {sample.get('rating', 'N/A')}")
            print(f"   - Content: {sample.get('content', 'N/A')[:100]}...")
        
        return len(reviews) > 0
        
    except Exception as e:
        print(f"❌ Direct scraper test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Sage and Capterra Backend Tests")
    print("=" * 50)
    
    # Test 1: Backend Health
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start the backend server first.")
        print("Command: cd backend && python integrated_review_scraper.py")
        return
    
    # Test 2: Direct Capterra Scraper
    direct_test = test_direct_capterra_scraper()
    
    # Test 3: API Endpoint - Capterra Scraping
    api_test = test_capterra_scraping()
    
    # Test 4: API Endpoint - Sentiment Analysis
    sentiment_test = test_sentiment_analysis()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Backend Health: PASSED")
    print(f"{'✅' if direct_test else '❌'} Direct Capterra Scraper: {'PASSED' if direct_test else 'FAILED'}")
    print(f"{'✅' if api_test else '❌'} API Capterra Scraping: {'PASSED' if api_test else 'FAILED'}")
    print(f"{'✅' if sentiment_test else '❌'} Sentiment Analysis: {'PASSED' if sentiment_test else 'FAILED'}")
    
    if direct_test and api_test and sentiment_test:
        print("\n🎉 All tests passed! Sage and Capterra scraping is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 