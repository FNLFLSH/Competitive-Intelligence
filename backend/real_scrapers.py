import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Dict
import re

def scrape_g2_reviews_bs4(company_name: str, max_reviews: int = 50) -> List[Dict]:
    """
    Scrape G2 reviews using BeautifulSoup (no API)
    """
    reviews = []
    page = 1
    
    # Try different URL patterns for G2
    url_patterns = [
        f"https://www.g2.com/products/{company_name.lower().replace(' ', '-')}/reviews?page=",
        f"https://www.g2.com/search?utf8=%E2%9C%93&query={company_name.replace(' ', '+')}&page=",
        f"https://www.g2.com/products/{company_name.lower().replace(' ', '-')}/reviews",
        f"https://www.g2.com/search?query={company_name.replace(' ', '+')}"
    ]
    
    print(f"🔍 Scraping G2 reviews for: {company_name}")
    
    for base_url in url_patterns:
        if len(reviews) >= max_reviews:
            break
            
        try:
            # Add page number if URL supports it
            url = base_url + str(page) if "page=" in base_url else base_url
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 403:
                print(f"⚠️ Rate limited by G2, trying next URL pattern...")
                continue
            elif response.status_code != 200:
                print(f"❌ Failed to fetch G2 page: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for review blocks with multiple selectors
            review_blocks = soup.select(".paper.paper--neutral.p-lg.mb-0, [data-testid='review-card'], .review-card, .review, .gdReview")
            
            if not review_blocks:
                print(f"📄 No reviews found with current URL pattern, trying next...")
                continue
            
            print(f"✅ Found {len(review_blocks)} potential review blocks")
            
            for block in review_blocks:
                if len(reviews) >= max_reviews:
                    break
                    
                try:
                    # Extract review text with multiple selectors
                    content = ""
                    text_selectors = [".review-text", ".content", "[data-testid='review-text']", ".review-body", "p"]
                    
                    for selector in text_selectors:
                        text_elements = block.select(selector)
                        if text_elements:
                            content = text_elements[0].get_text(strip=True)
                            if content and len(content) > 10:  # Ensure meaningful content
                                break
                    
                    if not content or len(content) < 10:
                        continue
                    
                    # Extract rating
                    rating = 0.0
                    rating_selectors = [".rating", ".stars", "[data-testid='rating']", ".score"]
                    
                    for selector in rating_selectors:
                        rating_elements = block.select(selector)
                        if rating_elements:
                            rating_text = rating_elements[0].get("aria-label", "") or rating_elements[0].get_text()
                            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                            if rating_match:
                                rating = float(rating_match.group(1))
                                break
                    
                    # Extract reviewer info
                    reviewer_name = ""
                    reviewer_title = ""
                    reviewer_selectors = [".reviewer", ".author", "[data-testid='reviewer']", ".user-name"]
                    
                    for selector in reviewer_selectors:
                        reviewer_elements = block.select(selector)
                        if reviewer_elements:
                            reviewer_text = reviewer_elements[0].get_text()
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
                        "url": url,
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
                    print(f"Error extracting G2 review: {e}")
                    continue
            
            if reviews:
                print(f"✅ Successfully scraped {len(reviews)} G2 reviews for {company_name}")
                break  # Found reviews, stop trying other URL patterns
                
        except Exception as e:
            print(f"❌ Error with G2 URL pattern: {e}")
            continue
        
        page += 1
        time.sleep(2)  # Be respectful
    
    return reviews

def scrape_glassdoor_reviews_bs4(company_name: str, max_reviews: int = 50) -> List[Dict]:
    """
    Scrape Glassdoor reviews using BeautifulSoup (search by company)
    """
    reviews = []
    
    # Try different URL patterns for Glassdoor
    url_patterns = [
        f"https://www.glassdoor.com/Reviews/{company_name.replace(' ', '-')}-reviews-SRCH_KE0,{len(company_name)}.htm",
        f"https://www.glassdoor.com/Search/results.htm?keyword={company_name.replace(' ', '%20')}",
        f"https://www.glassdoor.com/Overview/{company_name.replace(' ', '-')}.htm"
    ]
    
    print(f"🔍 Scraping Glassdoor reviews for: {company_name}")
    
    for search_url in url_patterns:
        if len(reviews) >= max_reviews:
            break
            
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 403:
                print(f"⚠️ Rate limited by Glassdoor, trying next URL pattern...")
                continue
            elif response.status_code != 200:
                print(f"❌ Failed to fetch Glassdoor: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for review blocks with multiple selectors
            review_blocks = soup.select(".gdReview, [data-testid='review'], .review, .reviewCard")
            
            if not review_blocks:
                print(f"📄 No reviews found with current URL pattern, trying next...")
                continue
            
            print(f"✅ Found {len(review_blocks)} potential review blocks")
            
            for block in review_blocks:
                if len(reviews) >= max_reviews:
                    break
                    
                try:
                    # Extract pros and cons with multiple selectors
                    pros = ""
                    cons = ""
                    pros_selectors = [".pros .reviewBody", ".pros", ".pros-text"]
                    cons_selectors = [".cons .reviewBody", ".cons", ".cons-text"]
                    
                    for selector in pros_selectors:
                        pros_elements = block.select(selector)
                        if pros_elements:
                            pros = pros_elements[0].get_text(strip=True)
                            if pros:
                                break
                    
                    for selector in cons_selectors:
                        cons_elements = block.select(selector)
                        if cons_elements:
                            cons = cons_elements[0].get_text(strip=True)
                            if cons:
                                break
                    
                    # Combine pros and cons into content
                    content = f"Pros: {pros} | Cons: {cons}"
                    
                    if not content or content == "Pros:  | Cons: " or len(content) < 10:
                        continue
                    
                    # Extract rating with multiple selectors
                    rating = 0.0
                    rating_selectors = [".rating", ".stars", ".score", ".overallRating"]
                    
                    for selector in rating_selectors:
                        rating_elements = block.select(selector)
                        if rating_elements:
                            rating_text = rating_elements[0].get("aria-label", "") or rating_elements[0].get_text()
                            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                            if rating_match:
                                rating = float(rating_match.group(1))
                                break
                    
                    # Extract reviewer info with multiple selectors
                    reviewer_name = ""
                    reviewer_selectors = [".reviewer", ".author", ".user-name", ".reviewer-name"]
                    
                    for selector in reviewer_selectors:
                        reviewer_elements = block.select(selector)
                        if reviewer_elements:
                            reviewer_name = reviewer_elements[0].get_text(strip=True)
                            break
                    
                    review = {
                        "company": company_name,
                        "platform": "glassdoor",
                        "content": content,
                        "url": search_url,
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
                    print(f"Error extracting Glassdoor review: {e}")
                    continue
            
            if reviews:
                print(f"✅ Successfully scraped {len(reviews)} Glassdoor reviews for {company_name}")
                break  # Found reviews, stop trying other URL patterns
                
        except Exception as e:
            print(f"❌ Error with Glassdoor URL pattern: {e}")
            continue
        
        time.sleep(2)  # Be respectful
    
    return reviews

def analyze_sentiment_heuristic(reviews: List[Dict]) -> List[Dict]:
    """
    Analyze sentiment with VADER + heuristics
    """
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    
    analyzer = SentimentIntensityAnalyzer()
    
    def heuristic_boost(text: str, score: float) -> float:
        """Apply heuristic adjustments to sentiment score"""
        text_lower = text.lower()
        
        # Negative indicators
        if any(word in text_lower for word in ["bug", "slow", "crash", "error", "broken", "terrible", "awful"]):
            score -= 0.2
        if any(word in text_lower for word in ["expensive", "costly", "overpriced"]):
            score -= 0.1
            
        # Positive indicators
        if any(word in text_lower for word in ["easy", "great", "excellent", "amazing", "perfect", "love"]):
            score += 0.2
        if any(word in text_lower for word in ["fast", "quick", "efficient", "smooth"]):
            score += 0.1
            
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

def summarize_sentiment(company: str, reviews: List[Dict]) -> Dict:
    """
    Create aggregated sentiment summary per company
    """
    if not reviews:
        return {
            "company": company,
            "avg_sentiment_score": 0.0,
            "total_reviews": 0,
            "source_platforms": []
        }
    
    sentiment_total = sum(r.get("sentiment_score", 0) for r in reviews)
    num_reviews = len(reviews)
    avg_score = sentiment_total / num_reviews if num_reviews else 0
    
    platforms = list(set(r.get("platform", r.get("source", "")) for r in reviews))
    
    return {
        "company": company,
        "avg_sentiment_score": round(avg_score, 2),
        "total_reviews": num_reviews,
        "source_platforms": platforms
    }

def run_pipeline(company_list: List[str], max_reviews_per_platform: int = 25) -> List[Dict]:
    """
    Main pipeline runner - scrapes, analyzes, and summarizes
    """
    all_summaries = []
    
    for company in company_list:
        print(f"\n🔍 Processing company: {company}")
        
        # Scrape from both platforms
        g2_reviews = scrape_g2_reviews_bs4(company, max_reviews_per_platform)
        time.sleep(2)  # Be respectful
        
        glassdoor_reviews = scrape_glassdoor_reviews_bs4(company, max_reviews_per_platform)
        time.sleep(2)  # Be respectful
        
        all_reviews = g2_reviews + glassdoor_reviews
        
        if all_reviews:
            # Analyze sentiment
            enriched_reviews = analyze_sentiment_heuristic(all_reviews)
            
            # Create summary
            summary = summarize_sentiment(company, enriched_reviews)
            all_summaries.append(summary)
            
            print(f"✅ {company}: {summary['total_reviews']} reviews, avg sentiment: {summary['avg_sentiment_score']}")
        else:
            print(f"❌ No reviews found for {company}")
    
    return all_summaries 