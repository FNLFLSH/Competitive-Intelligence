#!/usr/bin/env python3
"""
Quick test to check which scraping sites are working
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_review_scraper import IntegratedReviewScraper

async def test_sites():
    print("🔍 QUICK SITE TESTING")
    print("=" * 50)
    
    # Test URLs
    test_urls = [
        ("Capterra - Sage", "https://www.capterra.com/p/110208/RDB-Pronet/"),
        ("Capterra - ADP", "https://www.capterra.com/p/ADP/"),
        ("G2 - Sage", "https://www.g2.com/products/sage-50cloud/reviews"),
        ("Glassdoor - Sage", "https://www.glassdoor.com/Reviews/Sage-Reviews-E1000.htm"),
    ]
    
    scraper = IntegratedReviewScraper()
    
    for site_name, url in test_urls:
        print(f"\n🔍 Testing: {site_name}")
        print(f"URL: {url}")
        
        try:
            if "capterra" in url.lower():
                # Test Capterra scraping
                reviews = await scraper.scrape_capterra_reviews_async("Test Company", url)
                if reviews:
                    print(f"✅ SUCCESS: Found {len(reviews)} reviews")
                    for i, review in enumerate(reviews[:2]):  # Show first 2
                        print(f"  Review {i+1}: {review.get('review_text', '')[:100]}...")
                else:
                    print("❌ NO REVIEWS FOUND")
            elif "g2" in url.lower():
                # Test G2 scraping
                reviews = scraper.scrape_g2_reviews("Test Company", url)
                if reviews:
                    print(f"✅ SUCCESS: Found {len(reviews)} reviews")
                    for i, review in enumerate(reviews[:2]):
                        print(f"  Review {i+1}: {review.get('review_text', '')[:100]}...")
                else:
                    print("❌ NO REVIEWS FOUND")
            elif "glassdoor" in url.lower():
                # Test Glassdoor scraping
                reviews = scraper.scrape_glassdoor_reviews("Test Company", url)
                if reviews:
                    print(f"✅ SUCCESS: Found {len(reviews)} reviews")
                    for i, review in enumerate(reviews[:2]):
                        print(f"  Review {i+1}: {review.get('review_text', '')[:100]}...")
                else:
                    print("❌ NO REVIEWS FOUND")
                    
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("-" * 40)
    
    print("\n🎯 TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_sites()) 