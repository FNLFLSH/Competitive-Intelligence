import os
import sys
import time
import json
import re
import uuid
import csv
from datetime import datetime
from typing import List, Dict, Optional, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import Playwright scrapers
from capterra_scraper import scrape_capterra_production
from production_scrapers import analyze_sentiment_production

# Add parent dir to path for utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.supabase_client import supabase

def load_company_urls_from_csv() -> Dict[str, Dict[str, str]]:
    """
    Load company URLs from the CSV file
    Returns: Dict with company name as key and URLs as value
    """
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "company_review_urls.csv")
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at: {csv_path}")
        return {}
    
    companies = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                company_name = row.get('Company', '').strip()
                capterra_url = row.get('Capterra_URL', '').strip()
                
                if company_name:
                    companies[company_name] = {
                        'capterra_url': capterra_url if capterra_url else None
                    }
        
        print(f"✅ Loaded {len(companies)} companies from CSV")
        return companies
        
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return {}

# Pydantic models matching frontend interfaces
class SentimentData(BaseModel):
    id: Optional[int] = None
    company: str
    platform: str  # 'g2' | 'glassdoor'
    title: Optional[str] = None
    content: str
    author: Optional[str] = None
    url: Optional[str] = None
    sentiment_score: Optional[float] = None  # -1.0 to 1.0
    sentiment_label: Optional[str] = None  # "positive" | "negative" | "neutral"
    sentiment_confidence: Optional[float] = None  # 0.0 to 1.0
    rating: Optional[float] = None  # 1-5 stars
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    reviewer_role: Optional[str] = None
    company_size: Optional[str] = None
    employment_status: Optional[str] = None
    recommendation: Optional[bool] = None
    review_date: Optional[str] = None
    scraped_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    raw_data: Optional[Dict] = None

class CompanyResult(BaseModel):
    company: str
    totalReviews: int
    averageSentiment: float  # -1.0 to 1.0
    averageRating: float  # 1.0 to 5.0
    platforms: Dict[str, Dict[str, Union[int, float]]]

class CompanySummary(BaseModel):
    totalReviews: int
    averageSentiment: float
    averageRating: float
    platformBreakdown: Dict[str, int]
    sentimentDistribution: Dict[str, int]

class ScrapingRequest(BaseModel):
    companies: List[str]

class ScrapingResult(BaseModel):
    success: bool
    totalReviews: int
    companiesProcessed: int
    platformBreakdown: Dict[str, int]
    averageSentiment: float
    storedInSupabase: bool
    storedCount: int
    processingTime: str
    errors: List[str]
    companyResults: List[CompanyResult]
    message: Optional[str] = None
    timestamp: Optional[str] = None
    requestId: Optional[str] = None

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

# Global scraping status
scraping_status = {
    "status": "idle",
    "message": "No scraping in progress",
    "progress": {},
    "total_reviews": 0,
    "timestamp": datetime.now().isoformat()
}

class IntegratedReviewScraper:
    def __init__(self, headless=True):
        """
        Integrated Review Scraper that works with existing Supabase setup
        
        Args:
            headless (bool): Run browser in headless mode
        """
        self.headless = headless
        self.driver = None
        self.mock_mode = False
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver with robust Windows compatibility"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless=new")  # Use new headless mode
            
            # Windows-specific options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
            
            # Additional Windows compatibility
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # Setup ChromeDriver with explicit path
            try:
                # Try to use ChromeDriverManager first
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                print(f"ChromeDriverManager failed: {e}")
                # Fallback to system Chrome
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Set window size and execute anti-detection script
            self.driver.set_window_size(1920, 1080)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Chrome WebDriver initialized successfully")
            self.mock_mode = False
            
        except Exception as e:
            print(f"❌ Chrome WebDriver failed to initialize: {e}")
            raise RuntimeError("Selenium Chrome WebDriver failed to initialize. Please check your Chrome/driver setup.")

    def mock_scrape_reviews(self, company_name: str, platform: str, max_reviews: int = 10) -> List[Dict]:
        """Mock scraping function that returns sample data"""
        import random
        
        sample_reviews = [
            {
                "review_text": f"Great product! {company_name} has really improved our workflow.",
                "reviewer_name": "John Doe",
                "rating": 4.5,
                "reviewer_title": "Software Engineer",
                "review_date": "2024-01-15",
                "pros": "Easy to use, good features",
                "cons": "Could be faster"
            },
            {
                "review_text": f"I'm satisfied with {company_name}. It meets our needs well.",
                "reviewer_name": "Jane Smith",
                "rating": 4.0,
                "reviewer_title": "Product Manager",
                "review_date": "2024-01-10",
                "pros": "Reliable, good support",
                "cons": "Price could be lower"
            },
            {
                "review_text": f"{company_name} is okay, but there's room for improvement.",
                "reviewer_name": "Bob Wilson",
                "rating": 3.5,
                "reviewer_title": "Business Analyst",
                "review_date": "2024-01-05",
                "pros": "Functional, stable",
                "cons": "Interface could be better"
            },
            {
                "review_text": f"Excellent experience with {company_name}! Highly recommended.",
                "reviewer_name": "Alice Brown",
                "rating": 5.0,
                "reviewer_title": "CTO",
                "review_date": "2024-01-20",
                "pros": "Powerful features, great ROI",
                "cons": "Learning curve"
            },
            {
                "review_text": f"{company_name} is decent but not exceptional.",
                "reviewer_name": "Charlie Davis",
                "rating": 3.0,
                "reviewer_title": "IT Manager",
                "review_date": "2024-01-12",
                "pros": "Works as advertised",
                "cons": "Limited customization"
            }
        ]
        
        reviews = []
        for i in range(min(max_reviews, len(sample_reviews))):
            review = sample_reviews[i].copy()
            review['company_name'] = company_name
            review['source'] = platform
            review['scraped_at'] = datetime.now().isoformat()
            
            # Analyze sentiment
            sentiment = self.analyze_sentiment(review['review_text'])
            review.update(sentiment)
            
            reviews.append(review)
        
        return reviews
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text using VADER"""
        try:
            scores = self.sentiment_analyzer.polarity_scores(text)
            
            # Determine sentiment label
            compound = scores['compound']
            if compound >= 0.05:
                label = "positive"
            elif compound <= -0.05:
                label = "negative"
            else:
                label = "neutral"
            
            return {
                'sentiment_score': compound,
                'sentiment_label': label,
                'sentiment_confidence': abs(compound),
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu']
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'sentiment_score': 0,
                'sentiment_label': "neutral",
                'sentiment_confidence': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 1
            }
    
    def store_reviews_in_supabase(self, reviews: List[Dict]) -> bool:
        """Store reviews in sentiment_data table with frontend-compatible format"""
        try:
            if not reviews:
                print("No reviews to store")
                return True
            
            # Transform reviews to match frontend SentimentData interface
            transformed_reviews = []
            for review in reviews:
                # Get sentiment score from either field
                sentiment_score = review.get("sentiment_score", review.get("sentiment_compound", 0.0))
                
                transformed_review = {
                    "company": review.get("company_name", ""),
                    "platform": review.get("source", ""),
                    "content": review.get("review_text", ""),
                    "author": review.get("reviewer_name", ""),
                    "rating": review.get("rating", 0.0),
                    "sentiment_score": sentiment_score,
                    "sentiment_label": self._get_sentiment_label(sentiment_score),
                    "sentiment_confidence": abs(sentiment_score),
                    "pros": [review.get("pros", "")] if review.get("pros") else [],
                    "cons": [review.get("cons", "")] if review.get("cons") else [],
                    "reviewer_role": review.get("reviewer_title", ""),
                    "review_date": review.get("review_date", ""),
                    "scraped_at": review.get("scraped_at", datetime.now().isoformat()),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                transformed_reviews.append(transformed_review)
            
            # Insert reviews into sentiment_data table
            result = supabase.table('sentiment_data').insert(transformed_reviews).execute()
            print(f"✅ Stored {len(transformed_reviews)} reviews in sentiment_data table")
            return True
            
        except Exception as e:
            print(f"❌ Error storing reviews in Supabase: {e}")
            return False
    
    def _get_sentiment_label(self, compound_score: float) -> str:
        """Convert compound score to sentiment label"""
        if compound_score >= 0.05:
            return "positive"
        elif compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    def scrape_capterra_reviews(self, company_name: str, capterra_url: str = None, max_reviews: int = 50) -> List[Dict]:
        """Scrape Capterra reviews using Playwright scraper"""
        from capterra_scraper import scrape_capterra_production
        reviews = scrape_capterra_production(company_name, max_reviews, capterra_url)
        # Optionally, run sentiment analysis here if not already done
        for review in reviews:
            sentiment = self.analyze_sentiment(review.get('content', ''))
            review['sentiment_score'] = sentiment['compound']
            review['sentiment_label'] = self._get_sentiment_label(sentiment['compound'])
        return reviews
    
    def scrape_g2_reviews(self, company_name: str, g2_url: str = None, max_reviews: int = 50) -> List[Dict]:
        """Scrape G2 reviews for a company (deprecated - using Capterra only)"""
        print(f"⚠️ G2 scraping deprecated for {company_name}, using Capterra only")
        return []
    
    def scrape_glassdoor_reviews(self, company_name: str, glassdoor_url: str = None, max_reviews: int = 50) -> List[Dict]:
        """Scrape Glassdoor reviews for a company (deprecated - using Capterra only)"""
        print(f"⚠️ Glassdoor scraping deprecated for {company_name}, using Capterra only")
        return []
    
    def extract_review_data(self, review_element) -> Dict:
        """Extract review data from review element"""
        try:
            # Extract review text
            review_text = ""
            text_elements = review_element.find_elements(By.CSS_SELECTOR, "[data-testid='review-text'], .review-text, .content")
            if text_elements:
                review_text = text_elements[0].text.strip()
            
            if not review_text:
                return None
            
            # Extract rating
            rating = 0.0
            rating_elements = review_element.find_elements(By.CSS_SELECTOR, "[data-testid='rating'], .rating, .stars")
            if rating_elements:
                rating_text = rating_elements[0].get_attribute('aria-label') or rating_elements[0].text
                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Extract reviewer info
            reviewer_name = ""
            reviewer_title = ""
            reviewer_elements = review_element.find_elements(By.CSS_SELECTOR, "[data-testid='reviewer'], .reviewer, .author")
            if reviewer_elements:
                reviewer_text = reviewer_elements[0].text
                reviewer_name = reviewer_text.split(' at ')[0] if ' at ' in reviewer_text else reviewer_text
            
            # Extract pros and cons
            pros = ""
            cons = ""
            pros_elements = review_element.find_elements(By.CSS_SELECTOR, "[data-testid='pros'], .pros")
            cons_elements = review_element.find_elements(By.CSS_SELECTOR, "[data-testid='cons'], .cons")
            
            if pros_elements:
                pros = pros_elements[0].text.strip()
            if cons_elements:
                cons = cons_elements[0].text.strip()
            
            return {
                'review_text': review_text,
                'rating': rating,
                'reviewer_name': reviewer_name,
                'reviewer_title': reviewer_title,
                'pros': pros,
                'cons': cons,
                'review_date': datetime.now().strftime("%Y-%m-%d")
            }
            
        except Exception as e:
            print(f"Error extracting review data: {e}")
            return None
    
    def close(self):
        """Close the webdriver"""
        if self.driver:
            self.driver.quit()

# Initialize FastAPI app
app = FastAPI(title="Review Scraper API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Review Scraper API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/scrape/live", response_model=ScrapingResult)
async def live_scraping(request: ScrapingRequest):
    """Live scraping endpoint matching frontend expectations"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Limit to 5 companies per request
    if len(request.companies) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 companies per request")
    
    try:
        # Load company URLs from CSV
        company_urls = load_company_urls_from_csv()
        if not company_urls:
            raise HTTPException(status_code=500, detail="Failed to load company URLs from CSV")
        
        # Perform scraping synchronously
        scraper = IntegratedReviewScraper(headless=True)
        all_reviews = []
        company_results = []
        errors = []
        
        print(f"🔍 Starting live scraping for companies: {request.companies}")
        
        for i, company in enumerate(request.companies):
            print(f"🔍 Scraping {company} ({i+1}/{len(request.companies)})")
            
            # Get URLs for this company from CSV
            company_data = company_urls.get(company, {})
            capterra_url = company_data.get('capterra_url')
            
            print(f"📋 URLs for {company}: Capterra={capterra_url}")
            
            company_reviews = []
            platform_stats = {"capterra": {"reviews": 0, "avgSentiment": 0, "avgRating": 0}}
            
            # Scrape from Capterra using URL from CSV
            if capterra_url:
                try:
                    reviews = scraper.scrape_capterra_reviews(company, capterra_url, 10) # Use Capterra URL from CSV
                    if reviews:
                        company_reviews.extend(reviews)
                        platform_stats["capterra"]["reviews"] = len(reviews)
                        if reviews:
                            platform_stats["capterra"]["avgSentiment"] = sum(r.get('sentiment_score', 0) for r in reviews) / len(reviews)
                            platform_stats["capterra"]["avgRating"] = sum(r.get('rating', 0) for r in reviews) / len(reviews)
                except Exception as e:
                    error_msg = f"Error scraping Capterra for {company}: {str(e)}"
                    print(f"❌ {error_msg}")
                    errors.append(error_msg)
            else:
                print(f"⚠️ No Capterra URL found for {company}, skipping...")
            
            if company_reviews:
                all_reviews.extend(company_reviews)
                
                # Calculate company stats
                total_reviews = len(company_reviews)
                avg_sentiment = sum(r.get('sentiment_score', 0) for r in company_reviews) / total_reviews
                avg_rating = sum(r.get('rating', 0) for r in company_reviews) / total_reviews
                
                company_result = CompanyResult(
                    company=company,
                    totalReviews=total_reviews,
                    averageSentiment=avg_sentiment,
                    averageRating=avg_rating,
                    platforms=platform_stats
                )
                company_results.append(company_result)
            
            # Delay between companies
            if i < len(request.companies) - 1:
                time.sleep(2)
        
        # Store in Supabase
        stored = scraper.store_reviews_in_supabase(all_reviews)
        
        # Calculate final stats
        total_reviews = len(all_reviews)
        avg_sentiment = sum(r.get('sentiment_score', 0) for r in all_reviews) / total_reviews if total_reviews > 0 else 0
        platform_breakdown = {"capterra": 0}
        
        for review in all_reviews:
            source = review.get('source', 'unknown')
            if source in platform_breakdown:
                platform_breakdown[source] += 1
        
        processing_time = f"{time.time() - start_time:.2f}s"
        
        print(f"✅ Scraping completed: {total_reviews} reviews stored")
        
        return ScrapingResult(
            success=True,
            totalReviews=total_reviews,
            companiesProcessed=len(request.companies),
            platformBreakdown=platform_breakdown,
            averageSentiment=avg_sentiment,
            storedInSupabase=stored,
            storedCount=len(all_reviews),
            processingTime=processing_time,
            errors=errors,
            companyResults=company_results,
            message=f"Scraped {total_reviews} reviews from {len(request.companies)} companies",
            timestamp=datetime.now().isoformat(),
            requestId=request_id
        )
        
    except Exception as e:
        error_msg = f"Scraping failed: {str(e)}"
        print(f"❌ {error_msg}")
        return ScrapingResult(
            success=False,
            totalReviews=0,
            companiesProcessed=0,
            platformBreakdown={"capterra": 0},
            averageSentiment=0.0,
            storedInSupabase=False,
            storedCount=0,
            processingTime="0s",
            errors=[error_msg],
            companyResults=[],
            message=error_msg,
            timestamp=datetime.now().isoformat(),
            requestId=request_id
        )
    finally:
        if 'scraper' in locals():
            scraper.close()

@app.post("/api/scrape/live-sentiment", response_model=ScrapingResult)
async def live_sentiment_scraping(request: ScrapingRequest):
    """Live sentiment scraping endpoint with enhanced features"""
    # This endpoint now uses the same synchronous scraping as live_scraping
    return await live_scraping(request)

@app.get("/api/scrape/live-sentiment")
async def get_sentiment_analysis(
    company: Optional[str] = Query(None),
    action: Optional[str] = Query(None)
):
    """Get sentiment analysis for specific company or recent data"""
    
    if action == "analysis" and company:
        # Get analysis for specific company
        try:
            result = supabase.table("sentiment_data").select("*").eq("company", company).execute()
            
            if result.data:
                reviews = result.data
                total_reviews = len(reviews)
                avg_sentiment = sum(r.get('sentiment_score', 0) for r in reviews) / total_reviews if total_reviews > 0 else 0
                avg_rating = sum(r.get('rating', 0) for r in reviews) / total_reviews if total_reviews > 0 else 0
                
                platform_breakdown = {}
                sentiment_distribution = {"positive": 0, "negative": 0, "neutral": 0}
                
                for review in reviews:
                    platform = review.get('platform', 'unknown')
                    platform_breakdown[platform] = platform_breakdown.get(platform, 0) + 1
                    
                    sentiment = review.get('sentiment_label', 'neutral')
                    sentiment_distribution[sentiment] += 1
                
                analysis = CompanySummary(
                    totalReviews=total_reviews,
                    averageSentiment=avg_sentiment,
                    averageRating=avg_rating,
                    platformBreakdown=platform_breakdown,
                    sentimentDistribution=sentiment_distribution
                )
                
                return {
                    "success": True,
                    "company": company,
                    "analysis": analysis.dict(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"No data found for company: {company}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error retrieving analysis: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    elif action == "recent":
        # Get recent scraped data
        try:
            result = supabase.table("sentiment_data").select("*").order("created_at", desc=True).limit(50).execute()
            
            return {
                "success": True,
                "recentData": result.data,
                "count": len(result.data),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error retrieving recent data: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    else:
        return {
            "success": False,
            "error": "Invalid action or missing parameters",
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint for AI interactions"""
    # This would integrate with your AI service
    # For now, return a simple response
    return {
        "success": True,
        "message": "Chat functionality would be integrated with your AI service",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/scrape/test")
async def test_scraping():
    """Test scraping endpoint"""
    return {
        "success": True,
        "message": "Test scraping endpoint",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/scrape/test")
async def get_test_status():
    """Get test scraping status"""
    return {
        "success": True,
        "status": "Test endpoint working",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/scrape/hiring")
async def hiring_scraping():
    """Hiring scraping endpoint"""
    return {
        "success": True,
        "message": "Hiring scraping endpoint",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/scrape/real")
async def real_scraping():
    """Real scraping endpoint"""
    return {
        "success": True,
        "message": "Real scraping endpoint",
        "timestamp": datetime.now().isoformat()
    }

async def run_scraping_task(companies: List[str], sources: List[str], max_reviews: int, headless: bool, request_id: str):
    """Run scraping task in background"""
    global scraping_status
    
    scraper = IntegratedReviewScraper(headless=headless)
    all_reviews = []
    company_results = []
    errors = []
    
    try:
        scraping_status = {
            "status": "running",
            "message": f"Scraping {len(companies)} companies",
            "progress": {},
            "total_reviews": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        for i, company in enumerate(companies):
            print(f"🔍 Scraping {company} ({i+1}/{len(companies)})")
            
            company_reviews = []
            platform_stats = {"capterra": {"reviews": 0, "avgSentiment": 0, "avgRating": 0}}
            
            # Use Capterra scraper for all companies
            try:
                # Get Capterra URL from CSV
                company_urls = load_company_urls_from_csv()
                capterra_url = company_urls.get(company, {}).get('capterra_url')
                
                print(f"📋 Using Capterra URL for {company}: {capterra_url}")
                
                # Use the Capterra scraper
                reviews = scraper.scrape_capterra_reviews(company, capterra_url, max_reviews)
                
                if reviews:
                    company_reviews.extend(reviews)
                    platform_stats["capterra"]["reviews"] = len(reviews)
                    if reviews:
                        platform_stats["capterra"]["avgSentiment"] = sum(r.get('sentiment_score', 0) for r in reviews) / len(reviews)
                        platform_stats["capterra"]["avgRating"] = sum(r.get('rating', 0) for r in reviews) / len(reviews)
                
                # Delay between companies
                time.sleep(3)
                
            except Exception as e:
                error_msg = f"Error scraping Capterra for {company}: {str(e)}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
            
            if company_reviews:
                all_reviews.extend(company_reviews)
                
                # Calculate company stats
                total_reviews = len(company_reviews)
                avg_sentiment = sum(r.get('sentiment_score', 0) for r in company_reviews) / total_reviews
                avg_rating = sum(r.get('rating', 0) for r in company_reviews) / total_reviews
                
                company_result = CompanyResult(
                    company=company,
                    totalReviews=total_reviews,
                    averageSentiment=avg_sentiment,
                    averageRating=avg_rating,
                    platforms=platform_stats
                )
                company_results.append(company_result)
            
            # Update progress
            scraping_status["progress"][company] = len(company_reviews)
            scraping_status["total_reviews"] = len(all_reviews)
            
            # Delay between companies
            if i < len(companies) - 1:
                time.sleep(3)
        
        # Store in Supabase
        stored = scraper.store_reviews_in_supabase(all_reviews)
        
        # Calculate final stats
        total_reviews = len(all_reviews)
        avg_sentiment = sum(r.get('sentiment_score', 0) for r in all_reviews) / total_reviews if total_reviews > 0 else 0
        platform_breakdown = {"capterra": 0}
        
        for review in all_reviews:
            source = review.get('source', 'unknown')
            if source in platform_breakdown:
                platform_breakdown[source] += 1
        
        processing_time = f"{time.time() - time.time():.2f}s"
        
        scraping_status = {
            "status": "completed",
            "message": f"Scraped {total_reviews} reviews from {len(companies)} companies",
            "progress": {company: len([r for r in all_reviews if r.get('company_name') == company]) for company in companies},
            "total_reviews": total_reviews,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ Scraping completed: {total_reviews} reviews stored")
        
    except Exception as e:
        error_msg = f"Scraping task failed: {str(e)}"
        print(f"❌ {error_msg}")
        errors.append(error_msg)
        scraping_status = {
            "status": "error",
            "message": error_msg,
            "progress": {},
            "total_reviews": 0,
            "timestamp": datetime.now().isoformat()
        }
    
    finally:
        scraper.close()

if __name__ == "__main__":
    print("🚀 Starting Review Scraper API...")
    print("📊 API will be available at: http://localhost:8000")
    print("📋 Available endpoints:")
    print("   POST /api/scrape/live")
    print("   POST /api/scrape/live-sentiment")
    print("   GET  /api/scrape/live-sentiment")
    print("   POST /api/chat")
    print("   GET  /health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 