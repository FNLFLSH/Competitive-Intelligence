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
                    },
                    {
                        "name": "Emma Wilson",
                        "rating": 5,
                        "content": "Excellent software! Sage has streamlined our entire accounting workflow. The cloud-based features are fantastic and the mobile app works perfectly. Highly recommend for any business.",
                        "role": "Accountant",
                        "pros": ["Cloud-based", "Mobile app", "Streamlined workflow"],
                        "cons": ["Initial setup time"]
                    },
                    {
                        "name": "David Thompson",
                        "rating": 4,
                        "content": "Very good accounting solution. The reporting features are comprehensive and the integration with other business tools is seamless. Customer service is excellent.",
                        "role": "CFO",
                        "pros": ["Comprehensive reporting", "Good integrations", "Excellent support"],
                        "cons": ["Complex for beginners"]
                    },
                    {
                        "name": "Lisa Rodriguez",
                        "rating": 3,
                        "content": "Decent accounting software with good basic features. The interface could be more user-friendly, but it gets the job done. Support is adequate.",
                        "role": "Bookkeeper",
                        "pros": ["Basic features work well", "Adequate support"],
                        "cons": ["Unfriendly interface", "Limited advanced features"]
                    },
                    {
                        "name": "James Anderson",
                        "rating": 5,
                        "content": "Outstanding accounting software! Sage has everything we need and more. The automation features are incredible and save us so much time. Best investment we've made.",
                        "role": "Small Business Owner",
                        "pros": ["Outstanding automation", "Time-saving", "Complete solution"],
                        "cons": ["Premium pricing"]
                    },
                    {
                        "name": "Rachel Green",
                        "rating": 4,
                        "content": "Great accounting software. The interface is intuitive and the reporting features are comprehensive. Customer support is responsive.",
                        "role": "Financial Manager",
                        "pros": ["Intuitive interface", "Comprehensive reporting", "Responsive support"],
                        "cons": ["Learning curve"]
                    },
                    {
                        "name": "Thomas Brown",
                        "rating": 4,
                        "content": "Solid accounting solution. The interface is clean and the features are comprehensive. Integration with our existing systems was smooth.",
                        "role": "IT Director",
                        "pros": ["Clean interface", "Comprehensive features", "Smooth integration"],
                        "cons": ["Could be faster"]
                    },
                    {
                        "name": "Amanda Davis",
                        "rating": 5,
                        "content": "Fantastic software! Sage has exceeded our expectations. The customer support team is incredibly helpful and the software is very reliable.",
                        "role": "Office Manager",
                        "pros": ["Exceeds expectations", "Helpful support", "Very reliable"],
                        "cons": ["None significant"]
                    },
                    {
                        "name": "Robert Wilson",
                        "rating": 3,
                        "content": "Good software overall. The basic accounting features work well, but some advanced features could be improved. Support is responsive.",
                        "role": "Business Analyst",
                        "pros": ["Good basic features", "Responsive support"],
                        "cons": ["Advanced features need improvement"]
                    },
                    {
                        "name": "Jennifer Lee",
                        "rating": 4,
                        "content": "Very reliable accounting software. The cloud backup is excellent and the multi-user features work perfectly for our team.",
                        "role": "Team Lead",
                        "pros": ["Reliable", "Excellent cloud backup", "Good multi-user"],
                        "cons": ["Interface could be better"]
                    },
                    {
                        "name": "Christopher Martinez",
                        "rating": 5,
                        "content": "Excellent choice for our business! Sage has all the features we need and the performance is outstanding. Highly recommend.",
                        "role": "Operations Manager",
                        "pros": ["All needed features", "Outstanding performance"],
                        "cons": ["Premium cost"]
                    },
                    {
                        "name": "Nicole Taylor",
                        "rating": 4,
                        "content": "Great accounting solution. The reporting capabilities are impressive and the data export features are very useful.",
                        "role": "Data Analyst",
                        "pros": ["Impressive reporting", "Useful export features"],
                        "cons": ["Complex setup"]
                    },
                    {
                        "name": "Kevin Johnson",
                        "rating": 3,
                        "content": "Decent software with good features. The interface is functional but could be more intuitive. Support is adequate.",
                        "role": "Accountant",
                        "pros": ["Good features", "Functional interface"],
                        "cons": ["Not very intuitive", "Adequate support"]
                    },
                    {
                        "name": "Stephanie White",
                        "rating": 5,
                        "content": "Outstanding software! Sage has transformed our accounting department. The automation features are incredible.",
                        "role": "Accounting Manager",
                        "pros": ["Transformed department", "Incredible automation"],
                        "cons": ["Learning period required"]
                    },
                    {
                        "name": "Daniel Clark",
                        "rating": 4,
                        "content": "Very good accounting software. The integration with our ERP system is seamless and the reporting is comprehensive.",
                        "role": "Systems Administrator",
                        "pros": ["Seamless ERP integration", "Comprehensive reporting"],
                        "cons": ["Complex configuration"]
                    },
                    {
                        "name": "Michelle Garcia",
                        "rating": 4,
                        "content": "Great software for our needs. The multi-currency support is excellent and the compliance features are very helpful.",
                        "role": "International Business Manager",
                        "pros": ["Excellent multi-currency", "Helpful compliance features"],
                        "cons": ["Complex for small businesses"]
                    },
                    {
                        "name": "Ryan Miller",
                        "rating": 5,
                        "content": "Fantastic accounting solution! Sage has everything we need and the customer support is exceptional.",
                        "role": "Business Owner",
                        "pros": ["Complete solution", "Exceptional support"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "Lauren Davis",
                        "rating": 4,
                        "content": "Very reliable accounting software. The backup and recovery features are excellent and the security is top-notch.",
                        "role": "Security Manager",
                        "pros": ["Excellent backup", "Top-notch security"],
                        "cons": ["Advanced features complex"]
                    },
                    {
                        "name": "Brandon Smith",
                        "rating": 4,
                        "content": "Good accounting software with solid features. The mobile app is excellent and the cloud sync works perfectly.",
                        "role": "Remote Worker",
                        "pros": ["Excellent mobile app", "Perfect cloud sync"],
                        "cons": ["Some features mobile-limited"]
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
                    },
                    {
                        "name": "John Smith",
                        "rating": 5,
                        "content": "Outstanding software! QuickBooks has everything we need and the automation features are incredible. Highly recommend for any business.",
                        "role": "Business Owner",
                        "pros": ["Complete solution", "Incredible automation"],
                        "cons": ["Premium pricing"]
                    },
                    {
                        "name": "Sarah Johnson",
                        "rating": 4,
                        "content": "Great accounting software. The interface is intuitive and the reporting features are comprehensive. Customer support is responsive.",
                        "role": "Accountant",
                        "pros": ["Intuitive interface", "Comprehensive reporting", "Responsive support"],
                        "cons": ["Learning curve"]
                    },
                    {
                        "name": "David Wilson",
                        "rating": 3,
                        "content": "Good software overall. The basic accounting features work well, but some advanced features could be improved. Support is adequate.",
                        "role": "Small Business Owner",
                        "pros": ["Good basic features", "Adequate support"],
                        "cons": ["Advanced features need work"]
                    },
                    {
                        "name": "Emily Brown",
                        "rating": 5,
                        "content": "Excellent choice! QuickBooks has streamlined our entire accounting process. The cloud features are fantastic.",
                        "role": "Office Manager",
                        "pros": ["Streamlined process", "Fantastic cloud features"],
                        "cons": ["Initial setup time"]
                    },
                    {
                        "name": "Michael Chen",
                        "rating": 4,
                        "content": "Very reliable accounting software. The bank reconciliation is flawless and the integration with other tools is seamless.",
                        "role": "Financial Manager",
                        "pros": ["Flawless reconciliation", "Seamless integration"],
                        "cons": ["Complex for beginners"]
                    },
                    {
                        "name": "Lisa Davis",
                        "rating": 4,
                        "content": "Great software with excellent features. The mobile app works perfectly and the cloud sync is reliable.",
                        "role": "Remote Worker",
                        "pros": ["Excellent mobile app", "Reliable cloud sync"],
                        "cons": ["Some mobile limitations"]
                    },
                    {
                        "name": "Robert Taylor",
                        "rating": 5,
                        "content": "Fantastic software! QuickBooks has exceeded our expectations. The customer support is exceptional.",
                        "role": "Business Owner",
                        "pros": ["Exceeds expectations", "Exceptional support"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "Amanda White",
                        "rating": 3,
                        "content": "Decent accounting software. The interface is functional but could be more user-friendly. Support is adequate.",
                        "role": "Bookkeeper",
                        "pros": ["Functional interface", "Adequate support"],
                        "cons": ["Not very user-friendly"]
                    },
                    {
                        "name": "Christopher Lee",
                        "rating": 4,
                        "content": "Very good accounting solution. The reporting capabilities are impressive and the data export features are useful.",
                        "role": "Data Analyst",
                        "pros": ["Impressive reporting", "Useful export features"],
                        "cons": ["Complex setup"]
                    },
                    {
                        "name": "Nicole Garcia",
                        "rating": 5,
                        "content": "Outstanding software! QuickBooks has transformed our accounting department completely.",
                        "role": "Accounting Manager",
                        "pros": ["Transformed department", "Complete solution"],
                        "cons": ["Learning period"]
                    },
                    {
                        "name": "Kevin Martinez",
                        "rating": 4,
                        "content": "Great accounting software. The integration with our existing systems was smooth and the features are comprehensive.",
                        "role": "IT Director",
                        "pros": ["Smooth integration", "Comprehensive features"],
                        "cons": ["Could be faster"]
                    },
                    {
                        "name": "Stephanie Clark",
                        "rating": 4,
                        "content": "Very reliable software. The backup features are excellent and the security is top-notch.",
                        "role": "Security Manager",
                        "pros": ["Excellent backup", "Top-notch security"],
                        "cons": ["Advanced features complex"]
                    },
                    {
                        "name": "Daniel Miller",
                        "rating": 5,
                        "content": "Excellent software! QuickBooks has everything we need and the performance is outstanding.",
                        "role": "Operations Manager",
                        "pros": ["Complete solution", "Outstanding performance"],
                        "cons": ["Premium cost"]
                    },
                    {
                        "name": "Michelle Smith",
                        "rating": 4,
                        "content": "Good accounting solution. The multi-currency support is excellent and the compliance features are helpful.",
                        "role": "International Business Manager",
                        "pros": ["Excellent multi-currency", "Helpful compliance"],
                        "cons": ["Complex for small businesses"]
                    },
                    {
                        "name": "Ryan Johnson",
                        "rating": 4,
                        "content": "Very good software. The mobile app is excellent and the cloud features work perfectly for our remote team.",
                        "role": "Team Lead",
                        "pros": ["Excellent mobile app", "Perfect cloud features"],
                        "cons": ["Some mobile limitations"]
                    },
                    {
                        "name": "Lauren Brown",
                        "rating": 5,
                        "content": "Fantastic accounting software! QuickBooks has made our accounting process so much easier.",
                        "role": "Business Owner",
                        "pros": ["Easier process", "Complete solution"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "Brandon Davis",
                        "rating": 3,
                        "content": "Decent software with good features. The interface could be more intuitive, but it gets the job done.",
                        "role": "Accountant",
                        "pros": ["Good features", "Gets job done"],
                        "cons": ["Not very intuitive"]
                    },
                    {
                        "name": "Jennifer Wilson",
                        "rating": 4,
                        "content": "Great accounting software. The automation features are excellent and save us a lot of time.",
                        "role": "Office Manager",
                        "pros": ["Excellent automation", "Time-saving"],
                        "cons": ["Learning curve"]
                    }
                ],
                "avg_rating": 4.0,
                "sentiment_score": 0.2
            },
            "Xero": {
                "reviews": [
                    {
                        "name": "Emma Thompson",
                        "rating": 5,
                        "content": "Xero is fantastic! The clean, modern interface is a breath of fresh air compared to other accounting software. The cloud-based features work seamlessly, and the mobile app is excellent.",
                        "role": "Small Business Owner",
                        "pros": ["Clean interface", "Modern design", "Excellent mobile app"],
                        "cons": ["Price"]
                    },
                    {
                        "name": "James Wilson",
                        "rating": 4,
                        "content": "Very good cloud accounting software. The bank reconciliation is excellent and the real-time updates are very helpful. Customer support is responsive.",
                        "role": "Accountant",
                        "pros": ["Excellent reconciliation", "Real-time updates", "Responsive support"],
                        "cons": ["Learning curve"]
                    },
                    {
                        "name": "Sophie Chen",
                        "rating": 5,
                        "content": "Outstanding software! Xero has transformed our accounting process. The automation features are incredible and save us hours every week.",
                        "role": "Office Manager",
                        "pros": ["Transformed process", "Incredible automation", "Time-saving"],
                        "cons": ["Premium pricing"]
                    },
                    {
                        "name": "Robert Davis",
                        "rating": 4,
                        "content": "Great cloud accounting solution. The multi-currency support is excellent and the integration with other business tools is seamless.",
                        "role": "International Business Manager",
                        "pros": ["Excellent multi-currency", "Seamless integration"],
                        "cons": ["Complex for beginners"]
                    },
                    {
                        "name": "Lisa Brown",
                        "rating": 3,
                        "content": "Good software overall. The interface is clean but some features could be more intuitive. Support is adequate.",
                        "role": "Bookkeeper",
                        "pros": ["Clean interface", "Adequate support"],
                        "cons": ["Not very intuitive"]
                    },
                    {
                        "name": "Michael Johnson",
                        "rating": 5,
                        "content": "Excellent choice! Xero has everything we need and the cloud features are fantastic. Highly recommend for any business.",
                        "role": "Business Owner",
                        "pros": ["Complete solution", "Fantastic cloud features"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "Amanda White",
                        "rating": 4,
                        "content": "Very reliable cloud accounting software. The backup features are excellent and the security is top-notch.",
                        "role": "Security Manager",
                        "pros": ["Excellent backup", "Top-notch security"],
                        "cons": ["Advanced features complex"]
                    },
                    {
                        "name": "David Taylor",
                        "rating": 4,
                        "content": "Great software with excellent features. The mobile app works perfectly and the cloud sync is reliable.",
                        "role": "Remote Worker",
                        "pros": ["Excellent mobile app", "Reliable cloud sync"],
                        "cons": ["Some mobile limitations"]
                    },
                    {
                        "name": "Nicole Garcia",
                        "rating": 5,
                        "content": "Fantastic software! Xero has exceeded our expectations. The customer support is exceptional.",
                        "role": "Business Owner",
                        "pros": ["Exceeds expectations", "Exceptional support"],
                        "cons": ["Premium cost"]
                    },
                    {
                        "name": "Christopher Lee",
                        "rating": 3,
                        "content": "Decent cloud accounting software. The basic features work well, but some advanced features could be improved.",
                        "role": "Small Business Owner",
                        "pros": ["Good basic features"],
                        "cons": ["Advanced features need work"]
                    },
                    {
                        "name": "Stephanie Clark",
                        "rating": 4,
                        "content": "Very good software. The reporting capabilities are impressive and the data export features are useful.",
                        "role": "Data Analyst",
                        "pros": ["Impressive reporting", "Useful export features"],
                        "cons": ["Complex setup"]
                    },
                    {
                        "name": "Daniel Miller",
                        "rating": 5,
                        "content": "Outstanding software! Xero has transformed our accounting department completely.",
                        "role": "Accounting Manager",
                        "pros": ["Transformed department", "Complete solution"],
                        "cons": ["Learning period"]
                    },
                    {
                        "name": "Michelle Smith",
                        "rating": 4,
                        "content": "Great cloud accounting software. The integration with our existing systems was smooth.",
                        "role": "IT Director",
                        "pros": ["Smooth integration", "Comprehensive features"],
                        "cons": ["Could be faster"]
                    },
                    {
                        "name": "Ryan Johnson",
                        "rating": 4,
                        "content": "Very reliable software. The cloud backup is excellent and the multi-user features work perfectly.",
                        "role": "Team Lead",
                        "pros": ["Excellent cloud backup", "Good multi-user"],
                        "cons": ["Interface could be better"]
                    },
                    {
                        "name": "Lauren Brown",
                        "rating": 5,
                        "content": "Fantastic cloud accounting software! Xero has made our accounting process so much easier.",
                        "role": "Business Owner",
                        "pros": ["Easier process", "Complete solution"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "Brandon Davis",
                        "rating": 3,
                        "content": "Decent software with good features. The interface could be more intuitive, but it gets the job done.",
                        "role": "Accountant",
                        "pros": ["Good features", "Gets job done"],
                        "cons": ["Not very intuitive"]
                    },
                    {
                        "name": "Jennifer Wilson",
                        "rating": 4,
                        "content": "Great cloud accounting software. The automation features are excellent and save us a lot of time.",
                        "role": "Office Manager",
                        "pros": ["Excellent automation", "Time-saving"],
                        "cons": ["Learning curve"]
                    },
                    {
                        "name": "Thomas Anderson",
                        "rating": 4,
                        "content": "Very good software. The mobile app is excellent and the cloud features work perfectly for our remote team.",
                        "role": "Remote Worker",
                        "pros": ["Excellent mobile app", "Perfect cloud features"],
                        "cons": ["Some mobile limitations"]
                    },
                    {
                        "name": "Rachel Green",
                        "rating": 5,
                        "content": "Excellent cloud accounting software! Xero has everything we need and the performance is outstanding.",
                        "role": "Operations Manager",
                        "pros": ["Complete solution", "Outstanding performance"],
                        "cons": ["Premium cost"]
                    },
                    {
                        "name": "Kevin Martinez",
                        "rating": 4,
                        "content": "Good cloud accounting solution. The multi-currency support is excellent and the compliance features are helpful.",
                        "role": "International Business Manager",
                        "pros": ["Excellent multi-currency", "Helpful compliance"],
                        "cons": ["Complex for small businesses"]
                    }
                ],
                "avg_rating": 4.1,
                "sentiment_score": 0.25
            },
            "Microsoft Dynamics": {
                "reviews": [
                    {
                        "name": "Alexander Thompson",
                        "rating": 4,
                        "content": "Microsoft Dynamics is a powerful enterprise solution with excellent integration capabilities. The reporting and analytics features are outstanding, and it scales well for large organizations.",
                        "role": "IT Director",
                        "pros": ["Powerful enterprise solution", "Excellent integration", "Outstanding analytics"],
                        "cons": ["Complex implementation", "Expensive"]
                    },
                    {
                        "name": "Sarah Johnson",
                        "rating": 3,
                        "content": "Good enterprise software with solid features. The implementation was complex but the functionality is comprehensive. Support is adequate.",
                        "role": "Business Analyst",
                        "pros": ["Comprehensive functionality", "Adequate support"],
                        "cons": ["Complex implementation", "Steep learning curve"]
                    },
                    {
                        "name": "Michael Chen",
                        "rating": 4,
                        "content": "Very reliable enterprise solution. The scalability is excellent and the integration with Microsoft products is seamless.",
                        "role": "Systems Administrator",
                        "pros": ["Excellent scalability", "Seamless Microsoft integration"],
                        "cons": ["Complex configuration"]
                    },
                    {
                        "name": "Emily Wilson",
                        "rating": 5,
                        "content": "Outstanding enterprise software! Dynamics has transformed our business processes completely. The automation features are incredible.",
                        "role": "Operations Manager",
                        "pros": ["Transformed processes", "Incredible automation"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "David Brown",
                        "rating": 4,
                        "content": "Great enterprise solution. The reporting capabilities are impressive and the data analytics are very powerful.",
                        "role": "Data Analyst",
                        "pros": ["Impressive reporting", "Powerful analytics"],
                        "cons": ["Complex setup"]
                    },
                    {
                        "name": "Lisa Davis",
                        "rating": 3,
                        "content": "Decent enterprise software. The features are comprehensive but the interface could be more user-friendly. Support is adequate.",
                        "role": "End User",
                        "pros": ["Comprehensive features", "Adequate support"],
                        "cons": ["Not very user-friendly"]
                    },
                    {
                        "name": "Robert Taylor",
                        "rating": 4,
                        "content": "Very good enterprise solution. The cloud deployment is excellent and the security features are top-notch.",
                        "role": "Security Manager",
                        "pros": ["Excellent cloud deployment", "Top-notch security"],
                        "cons": ["Advanced features complex"]
                    },
                    {
                        "name": "Amanda White",
                        "rating": 5,
                        "content": "Fantastic enterprise software! Dynamics has exceeded our expectations. The customer support is exceptional.",
                        "role": "Business Owner",
                        "pros": ["Exceeds expectations", "Exceptional support"],
                        "cons": ["Premium cost"]
                    },
                    {
                        "name": "Christopher Lee",
                        "rating": 4,
                        "content": "Great enterprise software. The integration with our existing systems was smooth and the features are comprehensive.",
                        "role": "IT Manager",
                        "pros": ["Smooth integration", "Comprehensive features"],
                        "cons": ["Could be faster"]
                    },
                    {
                        "name": "Nicole Garcia",
                        "rating": 3,
                        "content": "Good enterprise solution overall. The basic features work well, but some advanced features could be improved.",
                        "role": "Business User",
                        "pros": ["Good basic features"],
                        "cons": ["Advanced features need work"]
                    },
                    {
                        "name": "Stephanie Clark",
                        "rating": 4,
                        "content": "Very reliable enterprise software. The backup features are excellent and the disaster recovery is robust.",
                        "role": "IT Administrator",
                        "pros": ["Excellent backup", "Robust disaster recovery"],
                        "cons": ["Complex configuration"]
                    },
                    {
                        "name": "Daniel Miller",
                        "rating": 5,
                        "content": "Excellent enterprise software! Dynamics has everything we need and the performance is outstanding.",
                        "role": "Operations Director",
                        "pros": ["Complete solution", "Outstanding performance"],
                        "cons": ["Premium cost"]
                    },
                    {
                        "name": "Michelle Smith",
                        "rating": 4,
                        "content": "Great enterprise solution. The multi-currency support is excellent and the compliance features are very helpful.",
                        "role": "International Business Manager",
                        "pros": ["Excellent multi-currency", "Helpful compliance"],
                        "cons": ["Complex for small businesses"]
                    },
                    {
                        "name": "Ryan Johnson",
                        "rating": 4,
                        "content": "Very good enterprise software. The mobile app is excellent and the cloud features work perfectly for our remote team.",
                        "role": "Team Lead",
                        "pros": ["Excellent mobile app", "Perfect cloud features"],
                        "cons": ["Some mobile limitations"]
                    },
                    {
                        "name": "Lauren Brown",
                        "rating": 5,
                        "content": "Fantastic enterprise software! Dynamics has made our business processes so much more efficient.",
                        "role": "Business Owner",
                        "pros": ["More efficient processes", "Complete solution"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "Brandon Davis",
                        "rating": 3,
                        "content": "Decent enterprise software with good features. The interface could be more intuitive, but it gets the job done.",
                        "role": "End User",
                        "pros": ["Good features", "Gets job done"],
                        "cons": ["Not very intuitive"]
                    },
                    {
                        "name": "Jennifer Wilson",
                        "rating": 4,
                        "content": "Great enterprise software. The automation features are excellent and save us a lot of time.",
                        "role": "Process Manager",
                        "pros": ["Excellent automation", "Time-saving"],
                        "cons": ["Learning curve"]
                    },
                    {
                        "name": "Thomas Anderson",
                        "rating": 4,
                        "content": "Very good enterprise solution. The reporting capabilities are impressive and the analytics are very powerful.",
                        "role": "Business Intelligence Analyst",
                        "pros": ["Impressive reporting", "Powerful analytics"],
                        "cons": ["Complex setup"]
                    },
                    {
                        "name": "Rachel Green",
                        "rating": 5,
                        "content": "Outstanding enterprise software! Dynamics has transformed our entire business operations.",
                        "role": "CEO",
                        "pros": ["Transformed operations", "Complete solution"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "Kevin Martinez",
                        "rating": 4,
                        "content": "Excellent enterprise solution. The scalability is outstanding and the integration capabilities are very impressive.",
                        "role": "CTO",
                        "pros": ["Outstanding scalability", "Impressive integration"],
                        "cons": ["Complex implementation"]
                    }
                ],
                "avg_rating": 3.8,
                "sentiment_score": 0.1
            },
            "SAP": {
                "reviews": [
                    {
                        "name": "Benjamin Thompson",
                        "rating": 4,
                        "content": "SAP is the industry leader for enterprise solutions. Very powerful and reliable with excellent analytics and reporting capabilities. Perfect for large organizations.",
                        "role": "Enterprise Architect",
                        "pros": ["Industry leader", "Powerful and reliable", "Excellent analytics"],
                        "cons": ["Complex", "Expensive"]
                    },
                    {
                        "name": "Sophia Johnson",
                        "rating": 3,
                        "content": "Good enterprise software with comprehensive features. The implementation is complex but the functionality is very powerful. Support is adequate.",
                        "role": "Business Analyst",
                        "pros": ["Comprehensive features", "Powerful functionality", "Adequate support"],
                        "cons": ["Complex implementation", "Steep learning curve"]
                    },
                    {
                        "name": "William Chen",
                        "rating": 4,
                        "content": "Very reliable enterprise solution. The scalability is excellent and the integration capabilities are outstanding.",
                        "role": "Systems Administrator",
                        "pros": ["Excellent scalability", "Outstanding integration"],
                        "cons": ["Complex configuration"]
                    },
                    {
                        "name": "Olivia Wilson",
                        "rating": 5,
                        "content": "Outstanding enterprise software! SAP has transformed our business processes completely. The automation features are incredible.",
                        "role": "Operations Manager",
                        "pros": ["Transformed processes", "Incredible automation"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "James Brown",
                        "rating": 4,
                        "content": "Great enterprise solution. The reporting capabilities are impressive and the data analytics are very powerful.",
                        "role": "Data Analyst",
                        "pros": ["Impressive reporting", "Powerful analytics"],
                        "cons": ["Complex setup"]
                    },
                    {
                        "name": "Emma Davis",
                        "rating": 3,
                        "content": "Decent enterprise software. The features are comprehensive but the interface could be more user-friendly. Support is adequate.",
                        "role": "End User",
                        "pros": ["Comprehensive features", "Adequate support"],
                        "cons": ["Not very user-friendly"]
                    },
                    {
                        "name": "Lucas Taylor",
                        "rating": 4,
                        "content": "Very good enterprise solution. The cloud deployment is excellent and the security features are top-notch.",
                        "role": "Security Manager",
                        "pros": ["Excellent cloud deployment", "Top-notch security"],
                        "cons": ["Advanced features complex"]
                    },
                    {
                        "name": "Ava White",
                        "rating": 5,
                        "content": "Fantastic enterprise software! SAP has exceeded our expectations. The customer support is exceptional.",
                        "role": "Business Owner",
                        "pros": ["Exceeds expectations", "Exceptional support"],
                        "cons": ["Premium cost"]
                    },
                    {
                        "name": "Mason Lee",
                        "rating": 4,
                        "content": "Great enterprise software. The integration with our existing systems was smooth and the features are comprehensive.",
                        "role": "IT Manager",
                        "pros": ["Smooth integration", "Comprehensive features"],
                        "cons": ["Could be faster"]
                    },
                    {
                        "name": "Isabella Garcia",
                        "rating": 3,
                        "content": "Good enterprise solution overall. The basic features work well, but some advanced features could be improved.",
                        "role": "Business User",
                        "pros": ["Good basic features"],
                        "cons": ["Advanced features need work"]
                    },
                    {
                        "name": "Ethan Clark",
                        "rating": 4,
                        "content": "Very reliable enterprise software. The backup features are excellent and the disaster recovery is robust.",
                        "role": "IT Administrator",
                        "pros": ["Excellent backup", "Robust disaster recovery"],
                        "cons": ["Complex configuration"]
                    },
                    {
                        "name": "Mia Miller",
                        "rating": 5,
                        "content": "Excellent enterprise software! SAP has everything we need and the performance is outstanding.",
                        "role": "Operations Director",
                        "pros": ["Complete solution", "Outstanding performance"],
                        "cons": ["Premium cost"]
                    },
                    {
                        "name": "Noah Smith",
                        "rating": 4,
                        "content": "Great enterprise solution. The multi-currency support is excellent and the compliance features are very helpful.",
                        "role": "International Business Manager",
                        "pros": ["Excellent multi-currency", "Helpful compliance"],
                        "cons": ["Complex for small businesses"]
                    },
                    {
                        "name": "Sophia Johnson",
                        "rating": 4,
                        "content": "Very good enterprise software. The mobile app is excellent and the cloud features work perfectly for our remote team.",
                        "role": "Team Lead",
                        "pros": ["Excellent mobile app", "Perfect cloud features"],
                        "cons": ["Some mobile limitations"]
                    },
                    {
                        "name": "Liam Brown",
                        "rating": 5,
                        "content": "Fantastic enterprise software! SAP has made our business processes so much more efficient.",
                        "role": "Business Owner",
                        "pros": ["More efficient processes", "Complete solution"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "Zoe Davis",
                        "rating": 3,
                        "content": "Decent enterprise software with good features. The interface could be more intuitive, but it gets the job done.",
                        "role": "End User",
                        "pros": ["Good features", "Gets job done"],
                        "cons": ["Not very intuitive"]
                    },
                    {
                        "name": "Jackson Wilson",
                        "rating": 4,
                        "content": "Great enterprise software. The automation features are excellent and save us a lot of time.",
                        "role": "Process Manager",
                        "pros": ["Excellent automation", "Time-saving"],
                        "cons": ["Learning curve"]
                    },
                    {
                        "name": "Aria Anderson",
                        "rating": 4,
                        "content": "Very good enterprise solution. The reporting capabilities are impressive and the analytics are very powerful.",
                        "role": "Business Intelligence Analyst",
                        "pros": ["Impressive reporting", "Powerful analytics"],
                        "cons": ["Complex setup"]
                    },
                    {
                        "name": "Grayson Green",
                        "rating": 5,
                        "content": "Outstanding enterprise software! SAP has transformed our entire business operations.",
                        "role": "CEO",
                        "pros": ["Transformed operations", "Complete solution"],
                        "cons": ["Investment required"]
                    },
                    {
                        "name": "Layla Martinez",
                        "rating": 4,
                        "content": "Excellent enterprise solution. The scalability is outstanding and the integration capabilities are very impressive.",
                        "role": "CTO",
                        "pros": ["Outstanding scalability", "Impressive integration"],
                        "cons": ["Complex implementation"]
                    }
                ],
                "avg_rating": 3.5,
                "sentiment_score": 0.0
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