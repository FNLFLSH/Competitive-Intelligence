import os
import sys
import time
import json
import re
import uuid
import csv
from datetime import datetime
from typing import List, Dict, Optional, Union
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

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

class ProductionReviewScraper:
    def __init__(self, headless=True):
        """
        Production Review Scraper with dummy data for demo purposes
        
        Args:
            headless (bool): Run browser in headless mode (not used in production)
        """
        self.headless = headless
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        print("✅ Production scraper initialized with dummy data")
    
    def generate_dummy_reviews(self, company_name: str, platform: str, max_reviews: int = 20) -> List[Dict]:
        """Generate realistic dummy reviews for demo purposes"""
        import random
        
        # Company-specific dummy data with detailed reviews
        company_data = {
            "Sage": {
                "reviews": [
                    {
                        "name": "Sarah Johnson",
                        "rating": 5,
                        "content": "Sage has completely transformed our accounting processes. The automation features save us hours every month, and the reporting capabilities are outstanding. Customer support is responsive and helpful. Highly recommended for any small to medium business looking for reliable accounting software.",
                        "role": "Financial Controller",
                        "pros": ["Excellent automation", "Great reporting", "Responsive support"],
                        "cons": ["Learning curve", "Price could be lower"]
                    },
                    {
                        "name": "Michael Chen",
                        "rating": 4,
                        "content": "Good accounting software with solid features. The interface is intuitive and the integration with our bank accounts works seamlessly. Some advanced features could be better documented, but overall it's a reliable solution for our business needs.",
                        "role": "Business Owner",
                        "pros": ["Intuitive interface", "Good bank integration", "Reliable"],
                        "cons": ["Limited documentation", "Some bugs"]
                    }
                ],
                "avg_rating": 4.2,
                "sentiment_score": 0.3
            },
            "QuickBooks": {
                "reviews": [
                    {
                        "name": "Alex Thompson",
                        "rating": 5,
                        "content": "QuickBooks is the gold standard for accounting software. Everything works seamlessly, from bank reconciliation to payroll processing. The mobile app is excellent, and customer support is always helpful.",
                        "role": "Small Business Owner",
                        "pros": ["Seamless operation", "Excellent mobile app", "Great support"],
                        "cons": ["Price"]
                    },
                    {
                        "name": "Maria Rodriguez",
                        "rating": 4,
                        "content": "Very good accounting software with excellent features. The integration with banks and credit cards works perfectly. Some advanced features could be better documented, but overall it's a solid choice.",
                        "role": "Bookkeeper",
                        "pros": ["Excellent bank integration", "Good features", "Solid choice"],
                        "cons": ["Poor documentation", "Complex advanced features"]
                    }
                ],
                "avg_rating": 4.0,
                "sentiment_score": 0.2
            }
        }
        
        # Get company-specific data or use default
        company_info = company_data.get(company_name, {
            "reviews": [
                {
                    "name": "Generic User",
                    "rating": 3,
                    "content": "Good software overall. Works as advertised.",
                    "role": "Business Owner",
                    "pros": ["Functional", "Reliable"],
                    "cons": ["Could be better"]
                }
            ],
            "avg_rating": 3.5,
            "sentiment_score": 0.0
        })
        
        # Use the predefined reviews for the company
        reviews = []
        company_reviews = company_info["reviews"]
        
        # Take up to max_reviews from the predefined list
        for i, review_data in enumerate(company_reviews[:max_reviews]):
            # Analyze sentiment for the review content
            sentiment = self.analyze_sentiment(review_data["content"])
            
            review = {
                "company_name": company_name,
                "source": platform,
                "reviewer_name": review_data["name"],
                "rating": review_data["rating"],
                "content": review_data["content"],
                "title": f"Review {i+1}",
                "reviewer_title": review_data["role"],
                "review_date": datetime.now().strftime("%Y-%m-%d"),
                "pros": review_data["pros"],
                "cons": review_data["cons"],
                "sentiment_score": sentiment["sentiment_score"],
                "sentiment_label": sentiment["sentiment_label"],
                "sentiment_confidence": sentiment["sentiment_confidence"],
                "scraped_at": datetime.now().isoformat(),
                "url": f"https://www.capterra.com/p/{company_name.lower().replace(' ', '-')}/"
            }
            
            reviews.append(review)
        
        print(f"✅ Generated {len(reviews)} dummy reviews for {company_name}")
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
                    "content": review.get("content", ""),
                    "author": review.get("reviewer_name", ""),
                    "rating": review.get("rating", 0.0),
                    "sentiment_score": sentiment_score,
                    "sentiment_label": self._get_sentiment_label(sentiment_score),
                    "sentiment_confidence": abs(sentiment_score),
                    "pros": review.get("pros", []),
                    "cons": review.get("cons", []),
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
    
    def close(self):
        """Cleanup for production scraper"""
        print("✅ Production scraper cleanup completed")

# Initialize FastAPI app
app = FastAPI(title="Production Review Scraper API", version="1.0.0")

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
    return {"message": "Production Review Scraper API is running (Dummy Data)"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "mode": "production-demo"}

@app.post("/api/scrape/live", response_model=ScrapingResult)
async def live_scraping(request: ScrapingRequest):
    """Live scraping endpoint with dummy data for production demo"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Limit to 10 companies per request
    if len(request.companies) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 companies per request")
    
    try:
        # Load company URLs from CSV
        company_urls = load_company_urls_from_csv()
        if not company_urls:
            raise HTTPException(status_code=500, detail="Failed to load company URLs from CSV")
        
        # Perform scraping with dummy data
        scraper = ProductionReviewScraper(headless=True)
        all_reviews = []
        company_results = []
        errors = []
        
        print(f"🔍 Starting production demo scraping for companies: {request.companies}")
        
        for i, company in enumerate(request.companies):
            print(f"🔍 Generating dummy data for {company} ({i+1}/{len(request.companies)})")
            
            # Generate dummy reviews for Capterra
            try:
                reviews = scraper.generate_dummy_reviews(company, "Capterra", 20)
                if reviews:
                    all_reviews.extend(reviews)
                    print(f"✅ Generated {len(reviews)} dummy reviews for {company}")
                else:
                    print(f"⚠️ No dummy reviews generated for {company}")
                    
            except Exception as e:
                error_msg = f"Error generating dummy data for {company}: {str(e)}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
            
            # Calculate company stats
            company_reviews = [r for r in all_reviews if r.get('company_name') == company]
            if company_reviews:
                total_reviews = len(company_reviews)
                avg_sentiment = sum(r.get('sentiment_score', 0) for r in company_reviews) / total_reviews
                avg_rating = sum(r.get('rating', 0) for r in company_reviews) / total_reviews
                
                company_result = CompanyResult(
                    company=company,
                    totalReviews=total_reviews,
                    averageSentiment=avg_sentiment,
                    averageRating=avg_rating,
                    platforms={"capterra": {"reviews": total_reviews, "avgSentiment": avg_sentiment, "avgRating": avg_rating}}
                )
                company_results.append(company_result)
            
            # Simulate processing time
            time.sleep(1)
        
        # Store in Supabase
        stored = scraper.store_reviews_in_supabase(all_reviews)
        
        # Calculate final stats
        total_reviews = len(all_reviews)
        avg_sentiment = sum(r.get('sentiment_score', 0) for r in all_reviews) / total_reviews if total_reviews > 0 else 0
        platform_breakdown = {"capterra": total_reviews}
        
        processing_time = f"{time.time() - start_time:.2f}s"
        
        print(f"✅ Production demo completed: {total_reviews} dummy reviews generated")
        
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
            message=f"Generated {total_reviews} dummy reviews from {len(request.companies)} companies (Production Demo)",
            timestamp=datetime.now().isoformat(),
            requestId=request_id
        )
        
    except Exception as e:
        error_msg = f"Production demo failed: {str(e)}"
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

@app.post("/api/scrape/test-sage", response_model=ScrapingResult)
async def test_sage_scraping():
    """Enhanced test endpoint for Sage scraping with dummy data"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Use the production scraper with dummy data
        scraper = ProductionReviewScraper(headless=True)
        
        print(f"🔍 Production demo test scraping for Sage with 20 dummy reviews")
        
        # Generate dummy reviews for Sage
        reviews = scraper.generate_dummy_reviews("Sage", "Capterra", 20)
        
        if not reviews:
            print(f"⚠️ No dummy reviews generated for Sage")
            return ScrapingResult(
                success=False,
                totalReviews=0,
                companiesProcessed=0,
                platformBreakdown={"capterra": 0},
                averageSentiment=0.0,
                storedInSupabase=False,
                storedCount=0,
                processingTime="0s",
                errors=["Failed to generate dummy reviews"],
                companyResults=[],
                message="Failed to generate dummy reviews",
                timestamp=datetime.now().isoformat(),
                requestId=request_id
            )
        
        # Store reviews in Supabase
        stored = scraper.store_reviews_in_supabase(reviews)
        
        # Calculate stats
        total_reviews = len(reviews)
        avg_sentiment = sum(r.get('sentiment_score', 0) for r in reviews) / total_reviews if total_reviews > 0 else 0
        avg_rating = sum(r.get('rating', 0) for r in reviews) / total_reviews if total_reviews > 0 else 0
        
        company_result = CompanyResult(
            company="Sage",
            totalReviews=total_reviews,
            averageSentiment=avg_sentiment,
            averageRating=avg_rating,
            platforms={"capterra": {"reviews": total_reviews, "avgSentiment": avg_sentiment, "avgRating": avg_rating}}
        )
        
        processing_time = f"{time.time() - start_time:.2f}s"
        
        print(f"✅ Production demo test completed: {total_reviews} dummy reviews for Sage")
        
        return ScrapingResult(
            success=True,
            totalReviews=total_reviews,
            companiesProcessed=1,
            platformBreakdown={"capterra": total_reviews},
            averageSentiment=avg_sentiment,
            storedInSupabase=stored,
            storedCount=total_reviews,
            processingTime=processing_time,
            errors=[],
            companyResults=[company_result],
            message=f"Production demo test completed: {total_reviews} dummy reviews for Sage",
            timestamp=datetime.now().isoformat(),
            requestId=request_id
        )
        
    except Exception as e:
        error_msg = f"Production demo test failed: {str(e)}"
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

if __name__ == "__main__":
    print("🚀 Starting Production Review Scraper API (Dummy Data)...")
    print("📊 API will be available at: http://localhost:8000")
    print("📋 Available endpoints:")
    print("   POST /api/scrape/live")
    print("   POST /api/scrape/test-sage")
    print("   GET  /health")
    print("🎭 MODE: Production Demo with Dummy Data")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 