import requests
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict
import re

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

def scrape_g2_direct(g2_url: str, company_name: str, max_reviews: int = 25) -> List[Dict]:
    """
    Scrape G2 reviews from a direct URL
    """
    reviews = []
    
    print(f"🔍 Direct G2 scraping from: {g2_url}")
    
    try:
        # Add random delay
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(
            g2_url, 
            headers=get_headers(), 
            timeout=15,
            allow_redirects=True
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch G2 page: {response.status_code}")
            return reviews
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try multiple selectors for review blocks
        review_blocks = []
        selectors = [
            ".paper.paper--neutral.p-lg.mb-0",
            "[data-testid='review-card']", 
            ".review-card", 
            ".review",
            ".review-item",
            ".review-container"
        ]
        
        for selector in selectors:
            blocks = soup.select(selector)
            if blocks:
                review_blocks = blocks
                print(f"✅ Found {len(blocks)} review blocks with selector: {selector}")
                break
        
        if not review_blocks:
            print(f"📄 No review blocks found")
            return reviews
        
        # Extract reviews
        for block in review_blocks:
            if len(reviews) >= max_reviews:
                break
                
            try:
                # Extract review text
                content = ""
                text_selectors = [
                    ".review-text", 
                    ".content", 
                    "[data-testid='review-text']", 
                    ".review-body", 
                    "p", 
                    ".description",
                    ".review-content"
                ]
                
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
                rating_selectors = [
                    ".rating", 
                    ".stars", 
                    "[data-testid='rating']", 
                    ".score", 
                    ".star-rating",
                    ".review-rating"
                ]
                
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
                reviewer_selectors = [
                    ".reviewer", 
                    ".author", 
                    "[data-testid='reviewer']", 
                    ".user-name", 
                    ".reviewer-name",
                    ".reviewer-info"
                ]
                
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
                    "url": g2_url,
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
                print(f"✅ Extracted G2 review {len(reviews)}/{max_reviews}")
                
            except Exception as e:
                print(f"Error extracting review: {e}")
                continue
        
        print(f"✅ Direct G2 scraping completed: {len(reviews)} reviews")
        
    except Exception as e:
        print(f"❌ Error scraping G2: {e}")
    
    return reviews

def scrape_glassdoor_direct(glassdoor_url: str, company_name: str, max_reviews: int = 25) -> List[Dict]:
    """
    Scrape Glassdoor reviews from a direct URL
    """
    reviews = []
    
    print(f"🔍 Direct Glassdoor scraping from: {glassdoor_url}")
    
    try:
        # Add random delay
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(
            glassdoor_url, 
            headers=get_headers(), 
            timeout=15,
            allow_redirects=True
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch Glassdoor page: {response.status_code}")
            return reviews
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try multiple selectors for review blocks
        review_blocks = []
        selectors = [
            ".gdReview", 
            "[data-testid='review']", 
            ".review", 
            ".reviewCard",
            ".review-item",
            ".review-container"
        ]
        
        for selector in selectors:
            blocks = soup.select(selector)
            if blocks:
                review_blocks = blocks
                print(f"✅ Found {len(blocks)} review blocks with selector: {selector}")
                break
        
        if not review_blocks:
            print(f"📄 No review blocks found")
            return reviews
        
        # Extract reviews
        for block in review_blocks:
            if len(reviews) >= max_reviews:
                break
                
            try:
                # Extract pros and cons
                pros = ""
                cons = ""
                pros_selectors = [
                    ".pros .reviewBody", 
                    ".pros", 
                    ".pros-text", 
                    ".pros-content",
                    ".pros-section"
                ]
                cons_selectors = [
                    ".cons .reviewBody", 
                    ".cons", 
                    ".cons-text", 
                    ".cons-content",
                    ".cons-section"
                ]
                
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
                rating_selectors = [
                    ".rating", 
                    ".stars", 
                    ".score", 
                    ".overallRating", 
                    ".star-rating",
                    ".review-rating"
                ]
                
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
                reviewer_selectors = [
                    ".reviewer", 
                    ".author", 
                    ".user-name", 
                    ".reviewer-name", 
                    ".reviewer-info",
                    ".reviewer-details"
                ]
                
                for selector in reviewer_selectors:
                    elements = block.select(selector)
                    if elements:
                        reviewer_name = elements[0].get_text(strip=True)
                        break
                
                review = {
                    "company": company_name,
                    "platform": "glassdoor",
                    "content": content,
                    "url": glassdoor_url,
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
                print(f"✅ Extracted Glassdoor review {len(reviews)}/{max_reviews}")
                
            except Exception as e:
                print(f"Error extracting review: {e}")
                continue
        
        print(f"✅ Direct Glassdoor scraping completed: {len(reviews)} reviews")
        
    except Exception as e:
        print(f"❌ Error scraping Glassdoor: {e}")
    
    return reviews

def analyze_sentiment_direct(reviews: List[Dict]) -> List[Dict]:
    """
    Sentiment analysis for direct scrapers
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

def scrape_company_with_direct_links(company_name: str, g2_url: str = None, glassdoor_url: str = None, max_reviews_per_platform: int = 15) -> Dict:
    """
    Scrape a company using direct URLs for G2 and Glassdoor
    """
    all_reviews = []
    
    print(f"\n🔍 Direct scraping for: {company_name}")
    
    # Scrape G2 if URL provided
    if g2_url:
        g2_reviews = scrape_g2_direct(g2_url, company_name, max_reviews_per_platform)
        if g2_reviews:
            all_reviews.extend(g2_reviews)
        time.sleep(random.uniform(2, 4))
    
    # Scrape Glassdoor if URL provided
    if glassdoor_url:
        glassdoor_reviews = scrape_glassdoor_direct(glassdoor_url, company_name, max_reviews_per_platform)
        if glassdoor_reviews:
            all_reviews.extend(glassdoor_reviews)
        time.sleep(random.uniform(2, 4))
    
    if all_reviews:
        # Analyze sentiment
        enriched_reviews = analyze_sentiment_direct(all_reviews)
        
        # Create summary
        sentiment_total = sum(r.get("sentiment_score", 0) for r in enriched_reviews)
        num_reviews = len(enriched_reviews)
        avg_score = sentiment_total / num_reviews if num_reviews else 0
        
        platforms = list(set(r.get("platform", r.get("source", "")) for r in enriched_reviews))
        
        summary = {
            "company": company_name,
            "avg_sentiment_score": round(avg_score, 2),
            "total_reviews": num_reviews,
            "source_platforms": platforms,
            "reviews": enriched_reviews
        }
        
        print(f"✅ {company_name}: {summary['total_reviews']} reviews, avg sentiment: {summary['avg_sentiment_score']}")
        return summary
    else:
        print(f"❌ No reviews found for {company_name}")
        return {
            "company": company_name,
            "avg_sentiment_score": 0.0,
            "total_reviews": 0,
            "source_platforms": [],
            "reviews": []
        } 