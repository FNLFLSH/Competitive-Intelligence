#!/usr/bin/env python3
"""
Test the exact API flow to debug the issue
"""

import asyncio
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_review_scraper import IntegratedReviewScraper, load_company_urls_from_csv

async def test_api_flow():
    print("🔍 TESTING EXACT API FLOW")
    print("=" * 50)
    
    start_time = time.time()
    companies = ["Sage"]
    
    try:
        # Load company URLs from CSV
        company_urls = load_company_urls_from_csv()
        if not company_urls:
            print("❌ Failed to load company URLs from CSV")
            return
        
        # Perform scraping synchronously
        scraper = IntegratedReviewScraper(headless=True)
        all_reviews = []
        company_results = []
        errors = []
        
        print(f"🔍 Starting live scraping for companies: {companies}")
        
        for i, company in enumerate(companies):
            print(f"🔍 Scraping {company} ({i+1}/{len(companies)})")
            
            # Get URLs for this company from CSV
            company_data = company_urls.get(company, {})
            capterra_url = company_data.get('capterra_url')
            
            print(f"📋 URLs for {company}: Capterra={capterra_url}")
            
            company_reviews = []
            platform_stats = {"capterra": {"reviews": 0, "avgSentiment": 0, "avgRating": 0}}
            
            # Scrape from Capterra using URL from CSV
            if capterra_url:
                try:
                    print(f"🔍 Calling scrape_capterra_reviews_async for {company}...")
                    reviews = await scraper.scrape_capterra_reviews_async(company, capterra_url, 10)
                    print(f"📊 Reviews returned: {len(reviews) if reviews else 0}")
                    
                    if reviews:
                        print(f"✅ Found {len(reviews)} reviews for {company}")
                        company_reviews.extend(reviews)
                        platform_stats["capterra"]["reviews"] = len(reviews)
                        if reviews:
                            platform_stats["capterra"]["avgSentiment"] = sum(r.get('sentiment_score', 0) for r in reviews) / len(reviews)
                            platform_stats["capterra"]["avgRating"] = sum(r.get('rating', 0) for r in reviews) / len(reviews)
                    else:
                        print(f"❌ No reviews found for {company}")
                except Exception as e:
                    error_msg = f"Error scraping Capterra for {company}: {str(e)}"
                    print(f"❌ {error_msg}")
                    errors.append(error_msg)
            else:
                print(f"⚠️ No Capterra URL found for {company}, skipping...")
            
            if company_reviews:
                all_reviews.extend(company_reviews)
                print(f"✅ Added {len(company_reviews)} reviews to all_reviews")
            else:
                print(f"❌ No company_reviews to add")
            
            # Delay between companies
            if i < len(companies) - 1:
                time.sleep(2)
        
        # Calculate final stats
        total_reviews = len(all_reviews)
        print(f"📊 Final stats: total_reviews={total_reviews}")
        
        processing_time = f"{time.time() - start_time:.2f}s"
        print(f"⏱️ Processing time: {processing_time}")
        
        return {
            "success": True,
            "totalReviews": total_reviews,
            "companiesProcessed": len(companies),
            "processingTime": processing_time,
            "errors": errors
        }
        
    except Exception as e:
        error_msg = f"Scraping failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    result = asyncio.run(test_api_flow())
    print(f"\n🎯 FINAL RESULT: {result}") 