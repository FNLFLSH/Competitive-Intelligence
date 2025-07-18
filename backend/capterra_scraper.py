#!/usr/bin/env python3
"""
Capterra Scraper using Playwright
Enhanced with better error handling and configurable debug output
"""

import asyncio
import re
import os
from typing import List, Dict, Optional
from datetime import datetime
from playwright.async_api import async_playwright

# Import centralized debug configuration
from debug_config import get_debug_config

# Get debug configuration
DEBUG_CONFIG = get_debug_config()

def cleanup_debug_files():
    """Clean up old debug files"""
    if not DEBUG_CONFIG["cleanup_old_files"]:
        return
    
    debug_patterns = [
        "capterra_debug_*.png",
        "capterra_debug_*.html"
    ]
    
    for pattern in debug_patterns:
        import glob
        files = glob.glob(pattern)
        for file in files:
            try:
                os.remove(file)
                print(f"🧹 Cleaned up: {file}")
            except Exception as e:
                print(f"⚠️ Could not remove {file}: {e}")

async def handle_cookie_consent(page):
    """Handle cookie consent popups"""
    try:
        # Common cookie consent selectors
        cookie_selectors = [
            '[data-testid="cookie-banner-accept"]',
            '.cookie-accept',
            '#accept-cookies',
            '.cookie-consent-accept',
            '[aria-label*="Accept"]',
            'button:has-text("Accept")',
            'button:has-text("Accept All")',
            'button:has-text("I Accept")'
        ]
        
        for selector in cookie_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    await element.click()
                    await asyncio.sleep(1)
                    print("  🍪 Cookie consent handled")
                    break
            except:
                continue
    except Exception as e:
        print(f"  ⚠️ Cookie consent handling failed: {e}")

async def scrape_capterra_playwright(company_name: str, max_reviews: int = 25, capterra_url: str = None) -> List[Dict]:
    reviews = []
    print(f"🔍 Playwright Capterra scraping for: {company_name}")
    if capterra_url:
        url = capterra_url
    else:
        # Updated URL format for Capterra
        url = f"https://www.capterra.com/p/{company_name.lower().replace(' ', '-')}/"
    print(f"  Navigating to: {url}")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-plugins',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ])
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Set timeout to 30 seconds
            page.set_default_timeout(30000)
            
            try:
                await page.goto(url, wait_until='domcontentloaded')
                await handle_cookie_consent(page)
                await asyncio.sleep(3)
                
                # Get current URL to see where we ended up
                current_url = page.url
                print(f"  📍 Current URL: {current_url}")
                
                # Check if page loaded successfully
                page_title = await page.title()
                print(f"  📄 Page title: {page_title}")
                
                # Only save debug files if enabled
                if DEBUG_CONFIG["save_screenshots"] or DEBUG_CONFIG["save_html"]:
                    safe_name = company_name.replace(' ', '_').replace('&', 'and').replace('(', '').replace(')', '')
                    
                    if DEBUG_CONFIG["save_screenshots"]:
                        screenshot_path = f"capterra_debug_{safe_name}.png"
                        await page.screenshot(path=screenshot_path)
                        print(f"  🖼️ Screenshot saved to {screenshot_path}")
                    
                    if DEBUG_CONFIG["save_html"]:
                        html_path = f"capterra_debug_{safe_name}.html"
                        html_content = await page.content()
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        print(f"  📝 HTML saved to {html_path}")
                
                # Look for review elements with updated selectors
                review_selectors = [
                    '.e1xzmg0z.c1ofrhif.typo-10.mb-6.space-y-4.p-6.lg\\:space-y-8',  # Capterra review cards
                    '.review-card', '.review', '.review-item', '[data-testid="review"]', '.review-content', '.review-box', '.review-container'
                ]
                
                review_elements = []
                for selector in review_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            review_elements = elements
                            print(f"  ✅ Found {len(elements)} review elements with selector: {selector}")
                            break
                    except Exception as e:
                        print(f"  ⚠️ Selector {selector} failed: {e}")
                        continue
                
                if not review_elements:
                    print("  📄 No review elements found")
                    return reviews
                
                # Extract reviews
                for i, element in enumerate(review_elements[:max_reviews], 1):
                    try:
                        # Extract reviewer name
                        reviewer_name = "Anonymous"
                        name_selectors = [
                            '.typo-20.text-neutral-99.font-semibold',  # Capterra reviewer names
                            '.reviewer-name', '.author-name', '.reviewer', '.author', '[data-testid="reviewer-name"]', '.user-name'
                        ]
                        for selector in name_selectors:
                            try:
                                name_element = await element.query_selector(selector)
                                if name_element:
                                    name = await name_element.text_content()
                                    name = name.strip() if name else ""
                                    if name and len(name) > 0:
                                        reviewer_name = name
                                        break
                            except:
                                continue
                        
                        # Extract rating
                        rating = 0.0
                        rating_selectors = [
                            '[aria-label*="star"]',  # Capterra star ratings
                            '.rating', '.stars', '[data-testid="rating"]', '.score', '.star-rating'
                        ]
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
                        
                        # Extract review content
                        content = ""
                        text_selectors = [
                            'p',  # Direct paragraph content
                            '.review-text', '.content', '[data-testid="review-text"]', '.review-body', '.description'
                        ]
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
                        
                        # Extract review title
                        title = ""
                        title_selectors = ['.review-title', '.title', 'h3', 'h4', '.heading']
                        for selector in title_selectors:
                            try:
                                title_element = await element.query_selector(selector)
                                if title_element:
                                    title = await title_element.text_content()
                                    title = title.strip() if title else ""
                                    break
                            except:
                                continue
                        
                        if content and len(content) > 10:
                            review = {
                                "platform": "Capterra",
                                "company": company_name,
                                "reviewer_name": reviewer_name,
                                "rating": rating,
                                "content": content,
                                "title": title,
                                "date": datetime.now().strftime("%Y-%m-%d"),
                                "scraped_at": datetime.now().isoformat(),
                                "url": url
                            }
                            reviews.append(review)
                            print(f"  ✅ Extracted review {i}: {reviewer_name} - {rating} stars")
                        else:
                            print(f"  ⚠️ Review {i} has insufficient content")
                            
                    except Exception as e:
                        print(f"  ❌ Error extracting review {i}: {e}")
                        continue
                
                print(f"  📊 Total reviews extracted: {len(reviews)}")
                
            except Exception as e:
                print(f"  ❌ Error during scraping: {e}")
                return reviews
            finally:
                await browser.close()
                
    except Exception as e:
        print(f"  ❌ Browser error: {e}")
        return reviews
    
    return reviews

# Compatibility alias for legacy imports
scrape_capterra_production = scrape_capterra_playwright

# Clean up old debug files on import
cleanup_debug_files()

if __name__ == "__main__":
    # Test the scraper
    async def test():
        result = await scrape_capterra_playwright("Sage", max_reviews=5)
        print(f"Found {len(result)} reviews")
        for review in result:
            print(f"- {review['reviewer_name']}: {review['rating']} stars")
    
    asyncio.run(test()) 