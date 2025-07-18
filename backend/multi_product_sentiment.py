#!/usr/bin/env python3
"""
Multi-Product Sentiment Analysis Module
Integrates with existing backend architecture without major changes
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import your existing modules
from capterra_scraper import scrape_capterra_playwright
from company_products_mapping import COMPANY_PRODUCTS_MAPPING, get_companies, get_company_products

class MultiProductSentimentAnalyzer:
    """
    Analyzes sentiment across multiple products for a company
    Maintains compatibility with existing frontend expectations
    """
    
    def __init__(self):
        self.company_products = COMPANY_PRODUCTS_MAPPING
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment using VADER (your existing method)"""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentIntensityAnalyzer()
            scores = analyzer.polarity_scores(text)
            return scores['compound']
        except ImportError:
            return 0.0
    
    def calculate_overall_sentiment(self, product_sentiments: List[float]) -> Dict[str, Any]:
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
    
    async def analyze_company_sentiment(self, company_name: str) -> Dict[str, Any]:
        """
        Analyze sentiment for all products of a company
        Returns data structure compatible with your existing frontend
        """
        
        if company_name not in self.company_products:
            return {
                "error": f"No products found for company: {company_name}",
                "company": company_name,
                "success": False
            }
        
        company_data = {
            "company": company_name,
            "products": {},
            "overallSentiment": None,
            "totalReviews": 0,
            "platforms": {
                "capterra": 0,
                "g2": 0,
                "glassdoor": 0
            },
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        product_sentiments = []
        products = self.company_products[company_name]
        
        print(f"🔍 Analyzing {len(products)} products for {company_name}...")
        
        for product_name, url in products.items():
            try:
                print(f"  📊 Processing: {product_name}")
                
                # Scrape reviews for this product
                reviews = await scrape_capterra_playwright(product_name, max_reviews=10, capterra_url=url)
                
                if reviews:
                    print(f"    ✅ Found {len(reviews)} reviews")
                    
                    # Analyze sentiment for each review
                    product_sentiment_scores = []
                    for review in reviews:
                        if review.get('content'):
                            sentiment = self.analyze_sentiment(review['content'])
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
                            "url": url,
                            "recentReviews": reviews[:5]  # Keep recent reviews for drill-down
                        }
                        
                        company_data["platforms"]["capterra"] += len(reviews)
                        company_data["totalReviews"] += len(reviews)
                        
                        print(f"    📈 Product sentiment: {avg_product_sentiment:.3f}")
                    else:
                        print(f"    ❌ No sentiment data for {product_name}")
                else:
                    print(f"    ❌ No reviews found for {product_name}")
                
            except Exception as e:
                print(f"    ❌ Error scraping {product_name}: {str(e)}")
                # Continue with other products even if one fails
        
        # Calculate overall company sentiment
        company_data["overallSentiment"] = self.calculate_overall_sentiment(product_sentiments)
        
        return company_data
    
    async def analyze_multiple_companies(self, company_names: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple companies
        Returns list of company data structures
        """
        results = []
        
        for company_name in company_names:
            print(f"\n🏢 Analyzing sentiment for {company_name}...")
            result = await self.analyze_company_sentiment(company_name)
            results.append(result)
        
        return results
    
    async def analyze_all_companies(self) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for all companies
        Returns list of company data structures
        """
        all_companies = get_companies()
        return await self.analyze_multiple_companies(all_companies)

# Example usage that integrates with your existing API structure
async def get_company_sentiment_api(company_name: str) -> Dict[str, Any]:
    """
    API function that returns company sentiment data
    Compatible with your existing frontend expectations
    """
    analyzer = MultiProductSentimentAnalyzer()
    return await analyzer.analyze_company_sentiment(company_name)

# Example of how this integrates with your existing live-sentiment endpoint
async def enhanced_live_sentiment_api(companies: List[str]) -> Dict[str, Any]:
    """
    Enhanced version of your existing live-sentiment endpoint
    Supports multi-product sentiment analysis
    """
    analyzer = MultiProductSentimentAnalyzer()
    results = await analyzer.analyze_multiple_companies(companies)
    
    # Calculate overall statistics (compatible with your existing frontend)
    total_companies = len(results)
    successful_companies = len([r for r in results if r.get('success', False)])
    total_reviews = sum(r.get('totalReviews', 0) for r in results)
    
    # Calculate overall sentiment across all companies
    all_sentiments = []
    for result in results:
        if result.get('overallSentiment'):
            all_sentiments.append(result['overallSentiment']['score'])
    
    average_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0
    
    return {
        "success": True,
        "message": f"Successfully analyzed {successful_companies}/{total_companies} companies",
        "summary": {
            "totalCompanies": total_companies,
            "successfulCompanies": successful_companies,
            "totalReviews": total_reviews,
            "averageSentiment": average_sentiment,
            "results": results
        },
        "results": results
    }

# Test function
async def test_multi_product_analysis():
    """Test the multi-product sentiment analysis"""
    print("🧪 Testing Multi-Product Sentiment Analysis")
    print("=" * 50)
    
    analyzer = MultiProductSentimentAnalyzer()
    
    # Test companies with multiple products
    test_companies = ["Sage", "ADP", "BILL (Bill.com)", "Cegid", "Emburse"]
    
    for company_name in test_companies:
        print(f"\n🏢 Testing: {company_name}")
        result = await analyzer.analyze_company_sentiment(company_name)
        
        if result.get('success'):
            print(f"✅ Success: {result['company']}")
            print(f"📊 Total Reviews: {result['totalReviews']}")
            
            if result.get('overallSentiment'):
                overall = result['overallSentiment']
                print(f"📈 Overall Sentiment: {overall['score']:.3f} ({overall['label']})")
                print(f"📦 Products Analyzed: {overall['totalProducts']}")
            
            print(f"📋 Products:")
            for product_name, data in result.get('products', {}).items():
                sentiment_label = "positive" if data["sentiment"] > 0.1 else "negative" if data["sentiment"] < -0.1 else "neutral"
                print(f"  - {product_name}: {data['sentiment']:.3f} ({sentiment_label}) - {data['reviews']} reviews")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_multi_product_analysis()) 