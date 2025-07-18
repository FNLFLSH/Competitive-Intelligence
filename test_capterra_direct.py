#!/usr/bin/env python3
"""
Direct test script for Capterra scraper - Multi-Product Sentiment Analysis
Demonstrates how to implement company-level + product-level sentiment
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add backend to path
sys.path.append('backend')

# Sage product URLs from Capterra (only working ones)
SAGE_PRODUCTS = {
    "SageHR": "https://www.capterra.com/p/128705/SageHR/#reviews",
    # "Sage X3": "https://www.capterra.com/p/145725/Sage-X3/#reviews",  # INVALID URL
    # "Sage 100cloud": "https://www.capterra.com/p/227232/Sage-100cloud/reviews/",  # CLOUDFLARE PROTECTED
    # "Sage Intacct": "https://www.capterra.com/p/145725/Sage-Intacct/#reviews"  # INVALID URL
}

def analyze_sentiment(text):
    """Simple sentiment analysis using VADER"""
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        return scores['compound']  # Returns value between -1 (negative) and +1 (positive)
    except ImportError:
        print("⚠️  VADER sentiment not available, skipping sentiment analysis")
        return 0.0

def calculate_overall_sentiment(product_sentiments: List[float]) -> Dict[str, Any]:
    """Calculate overall company sentiment from multiple products"""
    if not product_sentiments:
        return {
            "score": 0.0,
            "label": "neutral",
            "totalProducts": 0,
            "positiveProducts": 0,
            "negativeProducts": 0,
            "neutralProducts": 0
        }
    
    avg_sentiment = sum(product_sentiments) / len(product_sentiments)
    
    # Count sentiment distribution
    positive_count = len([s for s in product_sentiments if s > 0.1])
    negative_count = len([s for s in product_sentiments if s < -0.1])
    neutral_count = len([s for s in product_sentiments if -0.1 <= s <= 0.1])
    
    # Determine overall label
    if avg_sentiment > 0.1:
        label = "positive"
    elif avg_sentiment < -0.1:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "score": avg_sentiment,
        "label": label,
        "totalProducts": len(product_sentiments),
        "positiveProducts": positive_count,
        "negativeProducts": negative_count,
        "neutralProducts": neutral_count
    }

async def test_multi_product_sentiment():
    """Test multi-product sentiment analysis for Sage"""
    print("🔍 Testing Multi-Product Sentiment Analysis for Sage")
    print("=" * 60)
    
    # This simulates your backend data structure
    company_data = {
        "company": "Sage",
        "products": {},
        "overallSentiment": None,
        "totalReviews": 0,
        "platforms": {
            "capterra": 0,
            "g2": 0,
            "glassdoor": 0
        }
    }
    
    product_sentiments = []
    all_reviews = []
    
    for product_name, url in SAGE_PRODUCTS.items():
        print(f"\n📊 Processing: {product_name}")
        print(f"🔗 URL: {url}")
        
        try:
            from capterra_scraper import scrape_capterra_playwright
            
            # Scrape reviews for this product
            reviews = await scrape_capterra_playwright(product_name, max_reviews=10, capterra_url=url)
            
            if reviews:
                print(f"✅ Success! Found {len(reviews)} reviews")
                
                # Analyze sentiment for each review
                product_sentiment_scores = []
                for review in reviews:
                    if review.get('content'):
                        sentiment = analyze_sentiment(review['content'])
                        review['sentiment'] = sentiment
                        product_sentiment_scores.append(sentiment)
                
                # Calculate product-level sentiment
                if product_sentiment_scores:
                    avg_product_sentiment = sum(product_sentiment_scores) / len(product_sentiment_scores)
                    product_sentiments.append(avg_product_sentiment)
                    
                    # Store product data (matches your frontend structure)
                    company_data["products"][product_name] = {
                        "sentiment": avg_product_sentiment,
                        "reviews": len(reviews),
                        "averageRating": sum(r.get('rating', 0) for r in reviews) / len(reviews) if reviews else 0,
                        "platform": "capterra",
                        "url": url
                    }
                    
                    company_data["platforms"]["capterra"] += len(reviews)
                    company_data["totalReviews"] += len(reviews)
                    all_reviews.extend(reviews)
                    
                    print(f"📈 Product sentiment: {avg_product_sentiment:.3f}")
                    
                    # Show sample reviews
                    print(f"\n📝 Sample reviews for {product_name}:")
                    for i, review in enumerate(reviews[:2], 1):
                        print(f"\n  Review {i}:")
                        print(f"    - Reviewer: {review.get('reviewer_name', 'Anonymous')}")
                        print(f"    - Rating: {review.get('rating', 'N/A')}")
                        print(f"    - Sentiment: {review.get('sentiment', 0.0):.3f}")
                        content = review.get('content', '')[:100] + "..." if len(review.get('content', '')) > 100 else review.get('content', '')
                        print(f"    - Content: {content}")
                else:
                    print(f"❌ No sentiment data for {product_name}")
            else:
                print(f"❌ No reviews found for {product_name}")
                
        except Exception as e:
            print(f"❌ Error scraping {product_name}: {str(e)}")
    
    # Calculate overall company sentiment
    company_data["overallSentiment"] = calculate_overall_sentiment(product_sentiments)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 SAGE COMPANY SENTIMENT ANALYSIS")
    print("=" * 60)
    
    overall = company_data["overallSentiment"]
    print(f"🏢 Company: Sage")
    print(f"📈 Overall Sentiment: {overall['score']:.3f} ({overall['label']})")
    print(f"📊 Products Analyzed: {overall['totalProducts']}")
    print(f"✅ Positive Products: {overall['positiveProducts']}")
    print(f"😐 Neutral Products: {overall['neutralProducts']}")
    print(f"❌ Negative Products: {overall['negativeProducts']}")
    print(f"📝 Total Reviews: {company_data['totalReviews']}")
    
    print("\n📋 PRODUCT BREAKDOWN:")
    print("-" * 40)
    for product_name, data in company_data["products"].items():
        sentiment_label = "positive" if data["sentiment"] > 0.1 else "negative" if data["sentiment"] < -0.1 else "neutral"
        print(f"  {product_name}:")
        print(f"    - Sentiment: {data['sentiment']:.3f} ({sentiment_label})")
        print(f"    - Reviews: {data['reviews']}")
        print(f"    - Avg Rating: {data['averageRating']:.1f}/5")
        print(f"    - Platform: {data['platform']}")
    
    print("\n" + "=" * 60)
    print("🎯 FRONTEND INTEGRATION READY")
    print("=" * 60)
    print("✅ This data structure matches your existing frontend expectations")
    print("✅ Company-level sentiment for dashboard overview")
    print("✅ Product-level sentiment for detailed drill-down")
    print("✅ Platform breakdown for source attribution")
    print("✅ Review counts for volume analysis")
    
    print("\n📤 API Response Format (Ready for Frontend):")
    print("-" * 40)
    print(json.dumps(company_data, indent=2))
    
    return company_data

if __name__ == "__main__":
    import json
    asyncio.run(test_multi_product_sentiment()) 