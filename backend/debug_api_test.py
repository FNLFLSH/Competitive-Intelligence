#!/usr/bin/env python3
"""
Debug script to test the exact API flow
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_review_scraper import IntegratedReviewScraper, load_company_urls_from_csv

async def debug_api_flow():
    print("🔍 DEBUGGING API FLOW")
    print("=" * 50)
    
    # Test the exact same flow as the API
    company = "Sage"
    
    # Load company URLs from CSV
    print(f"📋 Loading company URLs from CSV...")
    company_urls = load_company_urls_from_csv()
    print(f"✅ Loaded {len(company_urls)} companies from CSV")
    
    # Get URLs for Sage
    company_data = company_urls.get(company, {})
    capterra_url = company_data.get('capterra_url')
    print(f"📋 URLs for {company}: Capterra={capterra_url}")
    
    if not capterra_url:
        print(f"❌ No Capterra URL found for {company}")
        return
    
    # Create scraper
    print(f"🔧 Creating scraper...")
    scraper = IntegratedReviewScraper(headless=True)
    
    try:
        # Test the async scraping method
        print(f"🔍 Testing async scraping for {company}...")
        reviews = await scraper.scrape_capterra_reviews_async(company, capterra_url, 10)
        
        print(f"📊 Results:")
        print(f"  - Reviews found: {len(reviews)}")
        
        if reviews:
            print(f"  - First review: {reviews[0]}")
            print(f"  - Sentiment scores: {[r.get('sentiment_score', 'N/A') for r in reviews[:3]]}")
            print(f"  - Ratings: {[r.get('rating', 'N/A') for r in reviews[:3]]}")
        else:
            print(f"  ❌ No reviews returned")
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.close()

if __name__ == "__main__":
    asyncio.run(debug_api_flow()) 