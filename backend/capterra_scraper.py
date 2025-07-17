#!/usr/bin/env python3
"""
Playwright-based scraper for Capterra reviews
"""

import asyncio
import random
import json
from datetime import datetime
from typing import List, Dict
import re
from playwright.async_api import async_playwright

def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
    ]
    return random.choice(user_agents)

async def setup_stealth_page(page):
    await page.set_viewport_size({"width": 1920, "height": 1080})
    await page.set_extra_http_headers({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    await page.mouse.move(random.randint(100, 800), random.randint(100, 600))
    await asyncio.sleep(random.uniform(0.5, 2))
    await page.evaluate("window.scrollTo(0, Math.random() * 100)")
    await asyncio.sleep(random.uniform(0.3, 1))

async def handle_cookie_consent(page):
    selectors = [
        'button:has-text("Accept")',
        'button:has-text("Accept All")',
        'button:has-text("Allow")',
        'button:has-text("OK")',
        'button:has-text("Got it")',
        'button:has-text("I agree")',
        '[data-testid="cookie-accept"]',
        '.cookie-accept',
        '#accept-cookies',
        '.accept-cookies'
    ]
    for selector in selectors:
        try:
            button = await page.query_selector(selector)
            if button:
                await button.click()
                await asyncio.sleep(1)
                break
        except:
            continue

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
                '--user-agent=' + get_random_user_agent()
            ])
            page = await browser.new_page()
            await setup_stealth_page(page)
            await asyncio.sleep(random.uniform(2, 5))
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await handle_cookie_consent(page)
            await asyncio.sleep(3)
            screenshot_path = f"capterra_debug_{company_name.replace(' ', '_')}.png"
            html_path = f"capterra_debug_{company_name.replace(' ', '_')}.html"
            await page.screenshot(path=screenshot_path)
            html_content = await page.content()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  🖼️ Screenshot saved to {screenshot_path}")
            print(f"  📝 HTML saved to {html_path}")
            review_selectors = [
                '.review-card', '.review', '.review-item', '[data-testid="review"]', '.review-content', '.review-box', '.review-container'
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
            for i, element in enumerate(review_elements):
                if len(reviews) >= max_reviews:
                    break
                try:
                    content = ""
                    text_selectors = ['.review-text', '.content', '[data-testid="review-text"]', '.review-body', 'p', '.description']
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
                    rating = 0.0
                    rating_selectors = ['.rating', '.stars', '[data-testid="rating"]', '.score', '.star-rating']
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
                    reviewer_name = "Anonymous"
                    name_selectors = ['.reviewer-name', '.author-name', '.reviewer', '.author', '[data-testid="reviewer-name"]', '.user-name']
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
                    review_date = datetime.now().strftime("%Y-%m-%d")
                    date_selectors = ['.review-date', '.date', '.timestamp', '[data-testid="review-date"]', '.review-time']
                    for selector in date_selectors:
                        try:
                            date_element = await element.query_selector(selector)
                            if date_element:
                                date_text = await date_element.text_content()
                                if date_text:
                                    review_date = date_text.strip()
                                    break
                        except:
                            continue
                    title = ""
                    title_selectors = ['.review-title', '.title', 'h3', 'h4', '[data-testid="review-title"]']
                    for selector in title_selectors:
                        try:
                            title_element = await element.query_selector(selector)
                            if title_element:
                                title_text = await title_element.text_content()
                                title = title_text.strip() if title_text else ""
                                if title:
                                    break
                        except:
                            continue
                    review = {
                        "platform": "Capterra",
                        "company": company_name,
                        "reviewer_name": reviewer_name,
                        "rating": rating,
                        "content": content,
                        "title": title,
                        "date": review_date,
                        "scraped_at": datetime.now().isoformat(),
                        "url": url
                    }
                    reviews.append(review)
                    print(f"  ✅ Extracted review {len(reviews)}: {reviewer_name} - {rating} stars")
                except Exception as e:
                    print(f"  ❌ Error extracting review {i}: {e}")
                    continue
            await browser.close()
    except Exception as e:
        print(f"  ❌ Error during Capterra scraping: {e}")
    print(f"  📊 Total reviews extracted: {len(reviews)}")
    return reviews

def scrape_capterra_production(company_name: str, max_reviews: int = 25, capterra_url: str = None) -> List[Dict]:
    return asyncio.run(scrape_capterra_playwright(company_name, max_reviews, capterra_url))

if __name__ == "__main__":
    # Example test
    import sys
    company = sys.argv[1] if len(sys.argv) > 1 else "Slack"
    reviews = asyncio.run(scrape_capterra_playwright(company, max_reviews=5))
    print(json.dumps(reviews, indent=2)) 