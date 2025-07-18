#!/usr/bin/env python3
"""
Comprehensive Multi-Product Sentiment Analysis Test
Tests multiple companies and shows data structure ready for frontend
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append('backend')

from multi_product_sentiment import MultiProductSentimentAnalyzer
from company_products_mapping import get_companies_with_multiple_products

async def test_comprehensive_sentiment():
    """Test comprehensive multi-product sentiment analysis"""
    print("🚀 COMPREHENSIVE MULTI-PRODUCT SENTIMENT ANALYSIS")
    print("=" * 60)
    
    analyzer = MultiProductSentimentAnalyzer()
    
    # Get companies with multiple products for testing
    multi_product_companies = get_companies_with_multiple_products()
    test_companies = list(multi_product_companies.keys())[:5]  # Test first 5 companies
    
    print(f"📊 Testing {len(test_companies)} companies with multiple products:")
    for company in test_companies:
        products = multi_product_companies[company]
        print(f"  - {company}: {len(products)} products")
    
    print("\n" + "=" * 60)
    print("🔍 STARTING ANALYSIS")
    print("=" * 60)
    
    all_results = []
    
    for company_name in test_companies:
        print(f"\n🏢 Analyzing: {company_name}")
        print("-" * 40)
        
        result = await analyzer.analyze_company_sentiment(company_name)
        all_results.append(result)
        
        if result.get('success'):
            print(f"✅ Success: {result['company']}")
            print(f"📊 Total Reviews: {result['totalReviews']}")
            
            if result.get('overallSentiment'):
                overall = result['overallSentiment']
                print(f"📈 Overall Sentiment: {overall['score']:.3f} ({overall['label']})")
                print(f"📦 Products Analyzed: {overall['totalProducts']}")
                print(f"✅ Positive Products: {overall['positiveProducts']}")
                print(f"😐 Neutral Products: {overall['neutralProducts']}")
                print(f"❌ Negative Products: {overall['negativeProducts']}")
            
            print(f"\n📋 Product Breakdown:")
            for product_name, data in result.get('products', {}).items():
                sentiment_label = "positive" if data["sentiment"] > 0.1 else "negative" if data["sentiment"] < -0.1 else "neutral"
                print(f"  - {product_name}:")
                print(f"    Sentiment: {data['sentiment']:.3f} ({sentiment_label})")
                print(f"    Reviews: {data['reviews']}")
                print(f"    Avg Rating: {data['averageRating']:.1f}/5")
                print(f"    Platform: {data['platform']}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    # Generate comprehensive summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE SUMMARY")
    print("=" * 60)
    
    successful_companies = [r for r in all_results if r.get('success')]
    total_reviews = sum(r.get('totalReviews', 0) for r in successful_companies)
    total_products = sum(len(r.get('products', {})) for r in successful_companies)
    
    print(f"🏢 Companies Analyzed: {len(test_companies)}")
    print(f"✅ Successful Companies: {len(successful_companies)}")
    print(f"📦 Total Products: {total_products}")
    print(f"📝 Total Reviews: {total_reviews}")
    
    # Calculate overall sentiment across all companies
    all_sentiments = []
    for result in successful_companies:
        if result.get('overallSentiment'):
            all_sentiments.append(result['overallSentiment']['score'])
    
    if all_sentiments:
        overall_avg = sum(all_sentiments) / len(all_sentiments)
        print(f"📈 Overall Average Sentiment: {overall_avg:.3f}")
        
        positive_companies = len([s for s in all_sentiments if s > 0.1])
        negative_companies = len([s for s in all_sentiments if s < -0.1])
        neutral_companies = len([s for s in all_sentiments if -0.1 <= s <= 0.1])
        
        print(f"✅ Positive Companies: {positive_companies}")
        print(f"😐 Neutral Companies: {neutral_companies}")
        print(f"❌ Negative Companies: {negative_companies}")
    
    # Show data structure ready for frontend
    print("\n" + "=" * 60)
    print("🎯 FRONTEND-READY DATA STRUCTURE")
    print("=" * 60)
    
    frontend_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "totalCompanies": len(test_companies),
            "successfulCompanies": len(successful_companies),
            "totalProducts": total_products,
            "totalReviews": total_reviews,
            "overallSentiment": overall_avg if all_sentiments else 0.0
        },
        "companies": successful_companies
    }
    
    print("✅ Data structure ready for frontend integration:")
    print(json.dumps(frontend_data, indent=2))
    
    # Show example of how this integrates with your existing API
    print("\n" + "=" * 60)
    print("🔌 API INTEGRATION EXAMPLE")
    print("=" * 60)
    
    print("Your existing frontend can use this data structure:")
    print("1. Dashboard Overview: Show company-level sentiment")
    print("2. Company Drill-down: Show individual products")
    print("3. Product Details: Show individual reviews")
    print("4. Platform Attribution: Show review sources")
    
    return frontend_data

async def test_single_company_detailed(company_name: str = "Sage"):
    """Test detailed analysis for a single company"""
    print(f"🔍 DETAILED ANALYSIS FOR {company_name.upper()}")
    print("=" * 50)
    
    analyzer = MultiProductSentimentAnalyzer()
    result = await analyzer.analyze_company_sentiment(company_name)
    
    if result.get('success'):
        print(f"✅ Company: {result['company']}")
        print(f"📊 Total Reviews: {result['totalReviews']}")
        
        if result.get('overallSentiment'):
            overall = result['overallSentiment']
            print(f"📈 Overall Sentiment: {overall['score']:.3f} ({overall['label']})")
            print(f"📦 Products Analyzed: {overall['totalProducts']}")
        
        print(f"\n📋 Detailed Product Analysis:")
        for product_name, data in result.get('products', {}).items():
            sentiment_label = "positive" if data["sentiment"] > 0.1 else "negative" if data["sentiment"] < -0.1 else "neutral"
            print(f"\n  🏷️  {product_name}:")
            print(f"    📊 Sentiment: {data['sentiment']:.3f} ({sentiment_label})")
            print(f"    📝 Reviews: {data['reviews']}")
            print(f"    ⭐ Avg Rating: {data['averageRating']:.1f}/5")
            print(f"    🌐 Platform: {data['platform']}")
            print(f"    🔗 URL: {data['url']}")
            
            # Show sample reviews
            if data.get('recentReviews'):
                print(f"    📄 Sample Reviews:")
                for i, review in enumerate(data['recentReviews'][:2], 1):
                    print(f"      Review {i}: {review.get('reviewer_name', 'Anonymous')} - {review.get('rating', 'N/A')} stars")
                    print(f"        Sentiment: {review.get('sentiment', 0.0):.3f}")
                    content = review.get('content', '')[:80] + "..." if len(review.get('content', '')) > 80 else review.get('content', '')
                    print(f"        Content: {content}")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "detailed":
        # Run detailed analysis for a specific company
        company = sys.argv[2] if len(sys.argv) > 2 else "Sage"
        asyncio.run(test_single_company_detailed(company))
    else:
        # Run comprehensive analysis
        asyncio.run(test_comprehensive_sentiment()) 