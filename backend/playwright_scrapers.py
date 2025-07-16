#!/usr/bin/env python3
"""
Playwright-based scrapers for G2 and Glassdoor reviews
"""

import asyncio
import time
import random
from datetime import datetime
from typing import List, Dict
import re
import json
from playwright.async_api import async_playwright

def get_random_user_agent():
    """Get a random user agent to avoid detection"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
    ]
    return random.choice(user_agents)

async def setup_stealth_page(page):
    """Setup page with stealth measures to avoid detection"""
    # Set realistic viewport
    await page.set_viewport_size({"width": 1920, "height": 1080})
    
    # Add extra headers to look more like a real browser
    await page.set_extra_http_headers({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    # Add random mouse movements to simulate human behavior
    await page.mouse.move(random.randint(100, 800), random.randint(100, 600))
    await asyncio.sleep(random.uniform(0.5, 2))
    
    # Scroll a bit to simulate human browsing
    await page.evaluate("window.scrollTo(0, Math.random() * 100)")
    await asyncio.sleep(random.uniform(0.3, 1))

async def handle_cookie_consent(page):
    """Handle cookie consent popups"""
    try:
        # Common cookie consent selectors
        cookie_selectors = [
            'button[contains(text(), "Accept")]',
            'button[contains(text(), "Accept All")]',
            'button[contains(text(), "Allow")]',
            'button[contains(text(), "OK")]',
            'button[contains(text(), "Got it")]',
            'button[contains(text(), "I agree")]',
            '[data-testid="cookie-accept"]',
            '.cookie-accept',
            '#accept-cookies',
            '.accept-cookies'
        ]
        
        for selector in cookie_selectors:
            try:
                button = await page.query_selector(selector)
                if button:
                    await button.click()
                    print(f"  ✅ Clicked cookie consent: {selector}")
                    await asyncio.sleep(1)
                    break
            except:
                continue
    except Exception as e:
        print(f"  ⚠️ Cookie consent handling failed: {e}")

async def scrape_g2_playwright(company_name: str, max_reviews: int = 25, g2_url: str = None) -> List[Dict]:
    """
    Playwright-based G2 scraper
    """
    reviews = []
    
    print(f"🔍 Playwright G2 scraping for: {company_name}")
    
    # Determine URL to use
    if g2_url:
        url = g2_url
        print(f"  Using provided URL: {url}")
    else:
        url = f"https://www.g2.com/products/{company_name.lower().replace(' ', '-')}/reviews"
        print(f"  Using generated URL: {url}")
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--user-agent=' + get_random_user_agent()
                ]
            )
            
            page = await browser.new_page()
            
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Add random delay
            await asyncio.sleep(random.uniform(2, 5))
            
            # Navigate to page
            print(f"  Navigating to: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for content to load
            await asyncio.sleep(3)

            # DEBUG: Take screenshot and save HTML
            screenshot_path = f"g2_debug_{company_name.replace(' ', '_')}.png"
            html_path = f"g2_debug_{company_name.replace(' ', '_')}.html"
            await page.screenshot(path=screenshot_path)
            html_content = await page.content()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  🖼️ Screenshot saved to {screenshot_path}")
            print(f"  📝 HTML saved to {html_path}")
            
            # Try to find review elements
            review_selectors = [
                ".paper.paper--neutral.p-lg.mb-0",
                "[data-testid='review-card']",
                ".review-card",
                ".review",
                ".review-item",
                ".review-content"
            ]
            
            review_elements = []
            for selector in review_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    review_elements = elements
                    print(f"  ✅ Found {len(elements)} review elements with selector: {selector}")
                    break
            
            if not review_elements:
                print(f"  📄 No review elements found")
                await browser.close()
                return reviews
            
            # Extract reviews
            for i, element in enumerate(review_elements):
                if len(reviews) >= max_reviews:
                    break
                    
                try:
                    # Extract review text
                    content = ""
                    text_selectors = [".review-text", ".content", "[data-testid='review-text']", ".review-body", "p", ".description"]
                    
                    for selector in text_selectors:
                        try:
                            text_element = await element.query_selector(selector)
                            if text_element:
                                content = await text_element.text_content()
                                content = content.strip() if content else ""
                                if content and len(content) > 20:
                                    break
                        except:
                            continue
                    
                    if not content or len(content) < 20:
                        continue
                    
                    # Extract rating
                    rating = 0.0
                    rating_selectors = [".rating", ".stars", "[data-testid='rating']", ".score", ".star-rating"]
                    
                    for selector in rating_selectors:
                        try:
                            rating_element = await element.query_selector(selector)
                            if rating_element:
                                rating_text = await rating_element.get_attribute("aria-label") or await rating_element.text_content()
                                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                                if rating_match:
                                    rating = float(rating_match.group(1))
                                    break
                        except:
                            continue
                    
                    # Extract reviewer info
                    reviewer_name = ""
                    reviewer_selectors = [".reviewer", ".author", "[data-testid='reviewer']", ".user-name", ".reviewer-name"]
                    
                    for selector in reviewer_selectors:
                        try:
                            reviewer_element = await element.query_selector(selector)
                            if reviewer_element:
                                reviewer_text = await reviewer_element.text_content()
                                reviewer_name = reviewer_text.split(' at ')[0] if ' at ' in reviewer_text else reviewer_text
                                break
                        except:
                            continue
                    
                    # Extract pros and cons
                    pros = ""
                    cons = ""
                    
                    try:
                        pros_element = await element.query_selector(".pros, [data-testid='pros']")
                        if pros_element:
                            pros = await pros_element.text_content()
                            pros = pros.strip() if pros else ""
                    except:
                        pass
                    
                    try:
                        cons_element = await element.query_selector(".cons, [data-testid='cons']")
                        if cons_element:
                            cons = await cons_element.text_content()
                            cons = cons.strip() if cons else ""
                    except:
                        pass
                    
                    review = {
                        "company": company_name,
                        "platform": "g2",
                        "content": content,
                        "url": url,
                        "review_date": str(datetime.now().date()),
                        "review_text": content,
                        "rating": rating,
                        "reviewer_name": reviewer_name,
                        "reviewer_title": "",
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
            
            await browser.close()
        
    except Exception as e:
        print(f"  ❌ Error during G2 scraping: {e}")
        return reviews
    
    print(f"✅ Playwright G2 scraping completed: {len(reviews)} reviews")
    return reviews

async def scrape_glassdoor_playwright(company_name: str, max_reviews: int = 25, glassdoor_url: str = None) -> List[Dict]:
    """
    Playwright-based Glassdoor scraper
    """
    reviews = []
    
    print(f"🔍 Playwright Glassdoor scraping for: {company_name}")
    
    # Determine URL to use
    if glassdoor_url:
        url = glassdoor_url
        print(f"  Using provided URL: {url}")
    else:
        url = f"https://www.glassdoor.com/Reviews/{company_name.replace(' ', '-')}-reviews-SRCH_KE0,{len(company_name)}.htm"
        print(f"  Using generated URL: {url}")
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--user-agent=' + get_random_user_agent()
                ]
            )
            
            page = await browser.new_page()
            
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Add random delay
            await asyncio.sleep(random.uniform(2, 5))
            
            # Navigate to page
            print(f"  Navigating to: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for content to load
            await asyncio.sleep(3)

            # DEBUG: Take screenshot and save HTML
            screenshot_path = f"glassdoor_debug_{company_name.replace(' ', '_')}.png"
            html_path = f"glassdoor_debug_{company_name.replace(' ', '_')}.html"
            await page.screenshot(path=screenshot_path)
            html_content = await page.content()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  🖼️ Screenshot saved to {screenshot_path}")
            print(f"  📝 HTML saved to {html_path}")
            
            # Try to find review elements
            review_selectors = [
                ".gdReview",
                "[data-testid='review']",
                ".review",
                ".reviewCard",
                ".review-item",
                ".review-content"
            ]
            
            review_elements = []
            for selector in review_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    review_elements = elements
                    print(f"  ✅ Found {len(elements)} review elements with selector: {selector}")
                    break
            
            if not review_elements:
                print(f"  📄 No review elements found")
                await browser.close()
                return reviews
            
            # Extract reviews
            for i, element in enumerate(review_elements):
                if len(reviews) >= max_reviews:
                    break
                    
                try:
                    # Extract pros and cons
                    pros = ""
                    cons = ""
                    pros_selectors = [".pros .reviewBody", ".pros", ".pros-text", ".pros-content"]
                    cons_selectors = [".cons .reviewBody", ".cons", ".cons-text", ".cons-content"]
                    
                    for selector in pros_selectors:
                        try:
                            pros_element = await element.query_selector(selector)
                            if pros_element:
                                pros = await pros_element.text_content()
                                pros = pros.strip() if pros else ""
                                if pros:
                                    break
                        except:
                            continue
                    
                    for selector in cons_selectors:
                        try:
                            cons_element = await element.query_selector(selector)
                            if cons_element:
                                cons = await cons_element.text_content()
                                cons = cons.strip() if cons else ""
                                if cons:
                                    break
                        except:
                            continue
                    
                    # Combine pros and cons into content
                    content = f"Pros: {pros} | Cons: {cons}"
                    
                    if not content or content == "Pros:  | Cons: " or len(content) < 20:
                        continue
                    
                    # Extract rating
                    rating = 0.0
                    rating_selectors = [".rating", ".stars", ".score", ".overallRating", ".star-rating"]
                    
                    for selector in rating_selectors:
                        try:
                            rating_element = await element.query_selector(selector)
                            if rating_element:
                                rating_text = await rating_element.get_attribute("aria-label") or await rating_element.text_content()
                                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                                if rating_match:
                                    rating = float(rating_match.group(1))
                                    break
                        except:
                            continue
                    
                    # Extract reviewer info
                    reviewer_name = ""
                    reviewer_selectors = [".reviewer", ".author", ".user-name", ".reviewer-name", ".reviewer-info"]
                    
                    for selector in reviewer_selectors:
                        try:
                            reviewer_element = await element.query_selector(selector)
                            if reviewer_element:
                                reviewer_text = await reviewer_element.text_content()
                                reviewer_name = reviewer_text.strip() if reviewer_text else ""
                                break
                        except:
                            continue
                    
                    review = {
                        "company": company_name,
                        "platform": "glassdoor",
                        "content": content,
                        "url": url,
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
            
            await browser.close()
        
    except Exception as e:
        print(f"  ❌ Error during Glassdoor scraping: {e}")
        return reviews
    
    print(f"✅ Playwright Glassdoor scraping completed: {len(reviews)} reviews")
    return reviews

# Wrapper functions to make them compatible with existing code
def scrape_g2_production(company_name: str, max_reviews: int = 25, g2_url: str = None) -> List[Dict]:
    """Wrapper for G2 scraping that runs the async function"""
    return asyncio.run(scrape_g2_playwright(company_name, max_reviews, g2_url))

def scrape_glassdoor_production(company_name: str, max_reviews: int = 25, glassdoor_url: str = None) -> List[Dict]:
    """Wrapper for Glassdoor scraping that runs the async function"""
    return asyncio.run(scrape_glassdoor_playwright(company_name, max_reviews, glassdoor_url)) 