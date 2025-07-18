import requests
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict
import re
import json

def get_random_user_agent():
    """Get a random user agent to avoid detection"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"
    ]
    return random.choice(user_agents)

def get_headers():
    """Get headers that look like a real browser"""
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    }

def scrape_g2_production(company_name: str, max_reviews: int = 25, g2_url: str = None) -> List[Dict]:
    """
    Production G2 scraper with multiple fallback strategies
    """
    reviews = []
    
    print(f"🔍 Production G2 scraping for: {company_name}")
    
    # If specific URL is provided, use it as the primary strategy
    if g2_url:
        strategies = [
            {
                "name": "Provided G2 URL",
                "url": g2_url,
                "selectors": [".paper.paper--neutral.p-lg.mb-0", "[data-testid='review-card']", ".review-card", ".review"]
            }
        ]
    else:
        # Fallback strategies
    strategies = [
        {
            "name": "Direct Product Page",
            "url": f"https://www.g2.com/products/{company_name.lower().replace(' ', '-')}/reviews",
            "selectors": [".paper.paper--neutral.p-lg.mb-0", "[data-testid='review-card']", ".review-card", ".review"]
        },
        {
            "name": "Search Results",
            "url": f"https://www.g2.com/search?query={company_name.replace(' ', '+')}",
            "selectors": [".paper.paper--neutral.p-lg.mb-0", "[data-testid='review-card']", ".review-card", ".review"]
        },
        {
            "name": "Category Search",
            "url": f"https://www.g2.com/categories/{company_name.lower().replace(' ', '-')}",
            "selectors": [".paper.paper--neutral.p-lg.mb-0", "[data-testid='review-card']", ".review-card", ".review"]
        }
    ]
    
    for strategy in strategies:
        if len(reviews) >= max_reviews:
            break
            
        try:
            print(f"  Trying strategy: {strategy['name']}")
            
            # Add random delay
            time.sleep(random.uniform(2, 5))
            
            response = requests.get(
                strategy['url'], 
                headers=get_headers(), 
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 403:
                print(f"    ⚠️ Rate limited, trying next strategy...")
                continue
            elif response.status_code != 200:
                print(f"    ❌ HTTP {response.status_code}, trying next strategy...")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try multiple selectors
            review_blocks = []
            for selector in strategy['selectors']:
                blocks = soup.select(selector)
                if blocks:
                    review_blocks = blocks
                    print(f"    ✅ Found {len(blocks)} review blocks with selector: {selector}")
                    break
            
            if not review_blocks:
                print(f"    📄 No review blocks found, trying next strategy...")
                continue
            
            # Extract reviews
            for block in review_blocks:
                if len(reviews) >= max_reviews:
                    break
                    
                try:
                    # Extract review text
                    content = ""
                    text_selectors = [".review-text", ".content", "[data-testid='review-text']", ".review-body", "p", ".description"]
                    
                    for selector in text_selectors:
                        elements = block.select(selector)
                        if elements:
                            content = elements[0].get_text(strip=True)
                            if content and len(content) > 20:  # Ensure meaningful content
                                break
                    
                    if not content or len(content) < 20:
                        continue
                    
                    # Extract rating
                    rating = 0.0
                    rating_selectors = [".rating", ".stars", "[data-testid='rating']", ".score", ".star-rating"]
                    
                    for selector in rating_selectors:
                        elements = block.select(selector)
                        if elements:
                            rating_text = elements[0].get("aria-label", "") or elements[0].get_text()
                            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                            if rating_match:
                                rating = float(rating_match.group(1))
                                break
                    
                    # Extract reviewer info
                    reviewer_name = ""
                    reviewer_title = ""
                    reviewer_selectors = [".reviewer", ".author", "[data-testid='reviewer']", ".user-name", ".reviewer-name"]
                    
                    for selector in reviewer_selectors:
                        elements = block.select(selector)
                        if elements:
                            reviewer_text = elements[0].get_text()
                            reviewer_name = reviewer_text.split(' at ')[0] if ' at ' in reviewer_text else reviewer_text
                            break
                    
                    # Extract pros and cons
                    pros = ""
                    cons = ""
                    pros_elements = block.select(".pros, [data-testid='pros']")
                    cons_elements = block.select(".cons, [data-testid='cons']")
                    
                    if pros_elements:
                        pros = pros_elements[0].get_text(strip=True)
                    if cons_elements:
                        cons = cons_elements[0].get_text(strip=True)
                    
                    review = {
                        "company": company_name,
                        "platform": "g2",
                        "content": content,
                        "url": strategy['url'],
                        "review_date": str(datetime.now().date()),
                        "review_text": content,
                        "rating": rating,
                        "reviewer_name": reviewer_name,
                        "reviewer_title": reviewer_title,
                        "pros": pros,
                        "cons": cons,
                        "source": "g2",
                        "company_name": company_name,
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    reviews.append(review)
                    print(f"    ✅ Extracted G2 review {len(reviews)}/{max_reviews}")
                    
                except Exception as e:
                    print(f"    Error extracting review: {e}")
                    continue
            
            if reviews:
                print(f"    ✅ Strategy successful! Found {len(reviews)} reviews")
                break
                
        except Exception as e:
            print(f"    ❌ Strategy failed: {e}")
            continue
    
    print(f"✅ Production G2 scraping completed: {len(reviews)} reviews")
    return reviews

def scrape_glassdoor_production(company_name: str, max_reviews: int = 25, glassdoor_url: str = None) -> List[Dict]:
    """
    Production Glassdoor scraper with multiple fallback strategies
    """
    reviews = []
    
    print(f"🔍 Production Glassdoor scraping for: {company_name}")
    
    # If specific URL is provided, use it as the primary strategy
    if glassdoor_url:
        strategies = [
            {
                "name": "Provided Glassdoor URL",
                "url": glassdoor_url,
                "selectors": [".gdReview", "[data-testid='review']", ".review", ".reviewCard"]
            }
        ]
    else:
        # Fallback strategies
    strategies = [
        {
            "name": "Direct Company Page",
            "url": f"https://www.glassdoor.com/Overview/{company_name.replace(' ', '-')}.htm",
            "selectors": [".gdReview", "[data-testid='review']", ".review", ".reviewCard"]
        },
        {
            "name": "Search Results",
            "url": f"https://www.glassdoor.com/Search/results.htm?keyword={company_name.replace(' ', '%20')}",
            "selectors": [".gdReview", "[data-testid='review']", ".review", ".reviewCard"]
        },
        {
            "name": "Reviews Page",
            "url": f"https://www.glassdoor.com/Reviews/{company_name.replace(' ', '-')}-reviews-SRCH_KE0,{len(company_name)}.htm",
            "selectors": [".gdReview", "[data-testid='review']", ".review", ".reviewCard"]
        }
    ]
    
    for strategy in strategies:
        if len(reviews) >= max_reviews:
            break
            
        try:
            print(f"  Trying strategy: {strategy['name']}")
            
            # Add random delay
            time.sleep(random.uniform(2, 5))
            
            response = requests.get(
                strategy['url'], 
                headers=get_headers(), 
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 403:
                print(f"    ⚠️ Rate limited, trying next strategy...")
                continue
            elif response.status_code != 200:
                print(f"    ❌ HTTP {response.status_code}, trying next strategy...")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try multiple selectors
            review_blocks = []
            for selector in strategy['selectors']:
                blocks = soup.select(selector)
                if blocks:
                    review_blocks = blocks
                    print(f"    ✅ Found {len(blocks)} review blocks with selector: {selector}")
                    break
            
            if not review_blocks:
                print(f"    📄 No review blocks found, trying next strategy...")
                continue
            
            # Extract reviews
            for block in review_blocks:
                if len(reviews) >= max_reviews:
                    break
                    
                try:
                    # Extract pros and cons
                    pros = ""
                    cons = ""
                    pros_selectors = [".pros .reviewBody", ".pros", ".pros-text", ".pros-content"]
                    cons_selectors = [".cons .reviewBody", ".cons", ".cons-text", ".cons-content"]
                    
                    for selector in pros_selectors:
                        elements = block.select(selector)
                        if elements:
                            pros = elements[0].get_text(strip=True)
                            if pros:
                                break
                    
                    for selector in cons_selectors:
                        elements = block.select(selector)
                        if elements:
                            cons = elements[0].get_text(strip=True)
                            if cons:
                                break
                    
                    # Combine pros and cons into content
                    content = f"Pros: {pros} | Cons: {cons}"
                    
                    if not content or content == "Pros:  | Cons: " or len(content) < 20:
                        continue
                    
                    # Extract rating
                    rating = 0.0
                    rating_selectors = [".rating", ".stars", ".score", ".overallRating", ".star-rating"]
                    
                    for selector in rating_selectors:
                        elements = block.select(selector)
                        if elements:
                            rating_text = elements[0].get("aria-label", "") or elements[0].get_text()
                            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                            if rating_match:
                                rating = float(rating_match.group(1))
                                break
                    
                    # Extract reviewer info
                    reviewer_name = ""
                    reviewer_selectors = [".reviewer", ".author", ".user-name", ".reviewer-name", ".reviewer-info"]
                    
                    for selector in reviewer_selectors:
                        elements = block.select(selector)
                        if elements:
                            reviewer_name = elements[0].get_text(strip=True)
                            break
                    
                    review = {
                        "company": company_name,
                        "platform": "glassdoor",
                        "content": content,
                        "url": strategy['url'],
                        "review_date": str(datetime.now().date()),
                        "review_text": content,
                        "rating": rating,
                        "reviewer_name": reviewer_name,
                        "reviewer_title": "",
                        "pros": pros,
                        "cons": cons,
                        "source": "glassdoor",
                        "company_name": company_name,
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    reviews.append(review)
                    print(f"    ✅ Extracted Glassdoor review {len(reviews)}/{max_reviews}")
                    
                except Exception as e:
                    print(f"    Error extracting review: {e}")
                    continue
            
            if reviews:
                print(f"    ✅ Strategy successful! Found {len(reviews)} reviews")
                break
                
        except Exception as e:
            print(f"    ❌ Strategy failed: {e}")
            continue
    
    print(f"✅ Production Glassdoor scraping completed: {len(reviews)} reviews")
    return reviews

def analyze_sentiment_production(reviews: List[Dict]) -> List[Dict]:
    """
    Production sentiment analysis with VADER + heuristics
    """
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    
    analyzer = SentimentIntensityAnalyzer()
    
    def heuristic_boost(text: str, score: float) -> float:
        """Apply heuristic adjustments to sentiment score"""
        text_lower = text.lower()
        
        # Negative indicators
        if any(word in text_lower for word in ["bug", "slow", "crash", "error", "broken", "terrible", "awful", "horrible"]):
            score -= 0.2
        if any(word in text_lower for word in ["expensive", "costly", "overpriced", "pricey"]):
            score -= 0.1
        if any(word in text_lower for word in ["difficult", "hard", "complex", "confusing"]):
            score -= 0.15
            
        # Positive indicators
        if any(word in text_lower for word in ["easy", "great", "excellent", "amazing", "perfect", "love", "fantastic"]):
            score += 0.2
        if any(word in text_lower for word in ["fast", "quick", "efficient", "smooth", "responsive"]):
            score += 0.1
        if any(word in text_lower for word in ["intuitive", "user-friendly", "simple", "straightforward"]):
            score += 0.15
            
        # Clamp to [-1, 1] range
        return max(-1.0, min(1.0, score))
    
    for review in reviews:
        try:
            text = review.get("content", review.get("review_text", ""))
            if not text:
                continue
                
            # Get VADER sentiment
            vs = analyzer.polarity_scores(text)
            raw_score = vs["compound"]
            
            # Apply heuristics
            adjusted_score = heuristic_boost(text, raw_score)
            
            # Determine label
            if adjusted_score > 0.05:
                label = "positive"
            elif adjusted_score < -0.05:
                label = "negative"
            else:
                label = "neutral"
            
            # Update review with sentiment data
            review["sentiment_score"] = adjusted_score
            review["sentiment_label"] = label
            review["sentiment_confidence"] = abs(adjusted_score)
            review["positive"] = vs["pos"]
            review["negative"] = vs["neg"]
            review["neutral"] = vs["neu"]
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            review["sentiment_score"] = 0.0
            review["sentiment_label"] = "neutral"
            review["sentiment_confidence"] = 0.0
    
    return reviews

def run_production_pipeline(company_list: List[str], max_reviews_per_platform: int = 15) -> List[Dict]:
    """
    Production pipeline runner - scrapes, analyzes, and summarizes
    """
    all_summaries = []
    
    for company in company_list:
        print(f"\n🔍 Production processing: {company}")
        
        # Scrape from both platforms
        g2_reviews = scrape_g2_production(company, max_reviews_per_platform)
        time.sleep(random.uniform(3, 6))  # Random delay between platforms
        
        glassdoor_reviews = scrape_glassdoor_production(company, max_reviews_per_platform)
        time.sleep(random.uniform(3, 6))  # Random delay between companies
        
        all_reviews = g2_reviews + glassdoor_reviews
        
        if all_reviews:
            # Analyze sentiment
            enriched_reviews = analyze_sentiment_production(all_reviews)
            
            # Create summary
            sentiment_total = sum(r.get("sentiment_score", 0) for r in enriched_reviews)
            num_reviews = len(enriched_reviews)
            avg_score = sentiment_total / num_reviews if num_reviews else 0
            
            platforms = list(set(r.get("platform", r.get("source", "")) for r in enriched_reviews))
            
            summary = {
                "company": company,
                "avg_sentiment_score": round(avg_score, 2),
                "total_reviews": num_reviews,
                "source_platforms": platforms,
                "reviews": enriched_reviews
            }
            all_summaries.append(summary)
            
            print(f"✅ {company}: {summary['total_reviews']} reviews, avg sentiment: {summary['avg_sentiment_score']}")
        else:
            print(f"❌ No reviews found for {company}")
    
    return all_summaries 