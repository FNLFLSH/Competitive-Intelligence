#!/usr/bin/env python3
"""
CAPTCHA Solver Web Interface
Allows manual CAPTCHA solving through a web interface
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from playwright.async_api import async_playwright
import base64
import io
from PIL import Image

app = FastAPI(title="CAPTCHA Solver Interface")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for CAPTCHA solving
captcha_state = {
    "current_captcha": None,
    "solved": False,
    "solution": None,
    "waiting": False
}

class CaptchaRequest(BaseModel):
    url: str
    company_name: str
    platform: str  # "g2" or "glassdoor"

class CaptchaSolution(BaseModel):
    solution: str
    captcha_id: str

@app.get("/", response_class=HTMLResponse)
async def get_captcha_solver_page():
    """Serve the CAPTCHA solver interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CAPTCHA Solver Interface</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .captcha-section { border: 1px solid #ccc; padding: 20px; margin: 20px 0; }
            .captcha-image { max-width: 100%; border: 1px solid #ddd; }
            .solution-input { width: 100%; padding: 10px; margin: 10px 0; font-size: 16px; }
            .button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            .button:hover { background: #0056b3; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .status.success { background: #d4edda; color: #155724; }
            .status.error { background: #f8d7da; color: #721c24; }
            .status.info { background: #d1ecf1; color: #0c5460; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 CAPTCHA Solver Interface</h1>
            
            <div class="captcha-section">
                <h2>Current Status</h2>
                <div id="status" class="status info">Waiting for CAPTCHA...</div>
            </div>
            
            <div class="captcha-section" id="captchaSection" style="display: none;">
                <h2>Solve CAPTCHA</h2>
                <p><strong>Company:</strong> <span id="companyName"></span></p>
                <p><strong>Platform:</strong> <span id="platform"></span></p>
                <p><strong>URL:</strong> <span id="url"></span></p>
                
                <div>
                    <img id="captchaImage" class="captcha-image" alt="CAPTCHA Image">
                </div>
                
                <div>
                    <input type="text" id="captchaSolution" class="solution-input" placeholder="Enter CAPTCHA solution...">
                    <button onclick="submitSolution()" class="button">Submit Solution</button>
                </div>
            </div>
            
            <div class="captcha-section">
                <h2>Start Scraping</h2>
                <button onclick="startScraping()" class="button">Start G2 Scraping for Sage</button>
                <button onclick="startGlassdoorScraping()" class="button">Start Glassdoor Scraping for Sage</button>
            </div>
            
            <div class="captcha-section">
                <h2>Logs</h2>
                <div id="logs" style="background: #f8f9fa; padding: 10px; height: 200px; overflow-y: scroll; font-family: monospace;"></div>
            </div>
        </div>
        
        <script>
            let ws = null;
            let currentCaptchaId = null;
            
            function connectWebSocket() {
                ws = new WebSocket('ws://localhost:8000/ws');
                
                ws.onopen = function() {
                    addLog('WebSocket connected');
                    updateStatus('Connected to server', 'success');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                };
                
                ws.onclose = function() {
                    addLog('WebSocket disconnected');
                    updateStatus('Disconnected from server', 'error');
                    setTimeout(connectWebSocket, 3000);
                };
            }
            
            function handleWebSocketMessage(data) {
                if (data.type === 'captcha_request') {
                    showCaptcha(data);
                } else if (data.type === 'scraping_status') {
                    addLog(data.message);
                } else if (data.type === 'scraping_complete') {
                    updateStatus('Scraping completed!', 'success');
                    addLog('Scraping completed with ' + data.review_count + ' reviews');
                }
            }
            
            function showCaptcha(data) {
                document.getElementById('captchaSection').style.display = 'block';
                document.getElementById('companyName').textContent = data.company_name;
                document.getElementById('platform').textContent = data.platform;
                document.getElementById('url').textContent = data.url;
                document.getElementById('captchaImage').src = 'data:image/png;base64,' + data.captcha_image;
                currentCaptchaId = data.captcha_id;
                updateStatus('CAPTCHA detected! Please solve it.', 'info');
                addLog('CAPTCHA detected for ' + data.company_name + ' on ' + data.platform);
            }
            
            function submitSolution() {
                const solution = document.getElementById('captchaSolution').value;
                if (!solution) {
                    alert('Please enter a solution');
                    return;
                }
                
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'captcha_solution',
                        solution: solution,
                        captcha_id: currentCaptchaId
                    }));
                    
                    document.getElementById('captchaSection').style.display = 'none';
                    document.getElementById('captchaSolution').value = '';
                    updateStatus('CAPTCHA solution submitted, continuing...', 'success');
                    addLog('CAPTCHA solution submitted: ' + solution);
                }
            }
            
            function startScraping() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'start_scraping',
                        platform: 'g2',
                        company_name: 'Sage'
                    }));
                    updateStatus('Starting G2 scraping...', 'info');
                    addLog('Starting G2 scraping for Sage');
                }
            }
            
            function startGlassdoorScraping() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'start_scraping',
                        platform: 'glassdoor',
                        company_name: 'Sage'
                    }));
                    updateStatus('Starting Glassdoor scraping...', 'info');
                    addLog('Starting Glassdoor scraping for Sage');
                }
            }
            
            function updateStatus(message, type) {
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = message;
                statusDiv.className = 'status ' + type;
            }
            
            function addLog(message) {
                const logsDiv = document.getElementById('logs');
                const timestamp = new Date().toLocaleTimeString();
                logsDiv.innerHTML += '[' + timestamp + '] ' + message + '\\n';
                logsDiv.scrollTop = logsDiv.scrollHeight;
            }
            
            // Connect on page load
            connectWebSocket();
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "start_scraping":
                await handle_scraping_request(websocket, message)
            elif message["type"] == "captcha_solution":
                await handle_captcha_solution(websocket, message)
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")

async def handle_scraping_request(websocket: WebSocket, message: Dict):
    """Handle scraping request from web interface"""
    platform = message.get("platform")
    company_name = message.get("company_name")
    
    await websocket.send_text(json.dumps({
        "type": "scraping_status",
        "message": f"Starting {platform} scraping for {company_name}..."
    }))
    
    # Start the scraping process
    if platform == "g2":
        await scrape_with_captcha_solving(websocket, company_name, "g2")
    elif platform == "glassdoor":
        await scrape_with_captcha_solving(websocket, company_name, "glassdoor")

async def handle_captcha_solution(websocket: WebSocket, message: Dict):
    """Handle CAPTCHA solution from web interface"""
    global captcha_state
    
    solution = message.get("solution")
    captcha_id = message.get("captcha_id")
    
    if captcha_state.get("current_captcha") == captcha_id:
        captcha_state["solution"] = solution
        captcha_state["solved"] = True
        captcha_state["waiting"] = False
        
        await websocket.send_text(json.dumps({
            "type": "scraping_status",
            "message": "CAPTCHA solution received, continuing scraping..."
        }))

async def scrape_with_captcha_solving(websocket: WebSocket, company_name: str, platform: str):
    """Scrape with CAPTCHA solving capability"""
    global captcha_state
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            )
            
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Determine URL based on platform
            if platform == "g2":
                url = f"https://www.g2.com/sellers/sage-software-d61a780c-4fb3-4781-9519-baa772f5ea91#reviews"
            else:  # glassdoor
                url = f"https://www.glassdoor.com/Reviews/Sage-Reviews-E1150.htm"
            
            await websocket.send_text(json.dumps({
                "type": "scraping_status",
                "message": f"Navigating to {platform} page..."
            }))
            
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Check for CAPTCHA
            captcha_detected = await check_for_captcha(page)
            
            if captcha_detected:
                await websocket.send_text(json.dumps({
                    "type": "scraping_status",
                    "message": "CAPTCHA detected! Waiting for solution..."
                }))
                
                # Take screenshot of CAPTCHA
                captcha_screenshot = await page.screenshot()
                captcha_image_b64 = base64.b64encode(captcha_screenshot).decode()
                
                captcha_id = f"captcha_{int(time.time())}"
                captcha_state["current_captcha"] = captcha_id
                captcha_state["waiting"] = True
                captcha_state["solved"] = False
                
                # Send CAPTCHA to web interface
                await websocket.send_text(json.dumps({
                    "type": "captcha_request",
                    "captcha_id": captcha_id,
                    "company_name": company_name,
                    "platform": platform,
                    "url": url,
                    "captcha_image": captcha_image_b64
                }))
                
                # Wait for CAPTCHA solution
                while captcha_state["waiting"]:
                    await asyncio.sleep(1)
                
                if captcha_state["solved"]:
                    # Enter CAPTCHA solution
                    solution = captcha_state["solution"]
                    await enter_captcha_solution(page, solution)
                    
                    await websocket.send_text(json.dumps({
                        "type": "scraping_status",
                        "message": "CAPTCHA solved, continuing..."
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "scraping_status",
                        "message": "CAPTCHA solving failed"
                    }))
                    await browser.close()
                    return
            
            # Continue with scraping
            await websocket.send_text(json.dumps({
                "type": "scraping_status",
                "message": "No CAPTCHA detected, proceeding with scraping..."
            }))
            
            # Wait a bit for page to load
            await asyncio.sleep(3)
            
            # Extract reviews (simplified for demo)
            reviews = await extract_reviews(page, platform)
            
            await websocket.send_text(json.dumps({
                "type": "scraping_complete",
                "review_count": len(reviews),
                "message": f"Scraping completed! Found {len(reviews)} reviews."
            }))
            
            await browser.close()
            
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "scraping_status",
            "message": f"Error during scraping: {str(e)}"
        }))

async def check_for_captcha(page) -> bool:
    """Check if CAPTCHA is present on the page"""
    captcha_selectors = [
        "iframe[src*='captcha']",
        "iframe[src*='recaptcha']",
        ".g-recaptcha",
        "#recaptcha",
        "[class*='captcha']",
        "[id*='captcha']"
    ]
    
    for selector in captcha_selectors:
        try:
            element = await page.query_selector(selector)
            if element:
                return True
        except:
            continue
    
    return False

async def enter_captcha_solution(page, solution: str):
    """Enter CAPTCHA solution"""
    # Look for CAPTCHA input field
    input_selectors = [
        "input[name*='captcha']",
        "input[id*='captcha']",
        "input[placeholder*='captcha']",
        "input[placeholder*='code']",
        "input[type='text']"
    ]
    
    for selector in input_selectors:
        try:
            input_field = await page.query_selector(selector)
            if input_field:
                await input_field.fill(solution)
                
                # Look for submit button
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Submit')",
                    "button:contains('Verify')"
                ]
                
                for submit_selector in submit_selectors:
                    try:
                        submit_button = await page.query_selector(submit_selector)
                        if submit_button:
                            await submit_button.click()
                            await asyncio.sleep(2)
                            return
                    except:
                        continue
        except:
            continue

async def extract_reviews(page, platform: str) -> list:
    """Extract reviews from the page"""
    reviews = []
    
    if platform == "g2":
        # G2 review selectors
        review_selectors = [
            ".paper.paper--neutral.p-lg.mb-0",
            "[data-testid='review-card']",
            ".review-card",
            ".review"
        ]
    else:
        # Glassdoor review selectors
        review_selectors = [
            ".gdReview",
            "[data-testid='review']",
            ".review",
            ".reviewCard"
        ]
    
    for selector in review_selectors:
        try:
            elements = await page.query_selector_all(selector)
            if elements:
                for element in elements[:5]:  # Limit to 5 reviews for demo
                    try:
                        text = await element.text_content()
                        if text and len(text) > 50:
                            reviews.append({
                                "content": text[:200] + "...",
                                "platform": platform
                            })
                    except:
                        continue
                break
        except:
            continue
    
    return reviews

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 