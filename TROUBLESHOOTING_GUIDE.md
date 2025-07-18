# 🔧 Technical Troubleshooting Guide

## 🚨 Common Errors & Solutions

### 1. **PowerShell Command Syntax Errors**

**Error**: `The token '&&' is not a valid statement separator`
```powershell
# BROKEN
cd backend && python main.py

# FIXED
cd backend; python main.py
# OR
cd backend
python main.py
```

**Solution**: Use `;` separator or separate commands in PowerShell

---

### 2. **Python Import Errors**

**Error**: `ModuleNotFoundError: No module named 'playwright'`
```bash
# Solution
pip install playwright
playwright install chromium
```

**Error**: `ModuleNotFoundError: No module named 'vaderSentiment'`
```bash
# Solution
pip install vaderSentiment
```

---

### 3. **CSS Selector Syntax Errors**

**Error**: `SyntaxError: Failed to execute 'querySelectorAll' on 'Document'`
```python
# BROKEN - Double backslashes
'.e1xzmg0z.c1ofrhif.typo-10.mb-6.space-y-4.p-6.lg\\\\:space-y-8'

# FIXED - Single backslash
'.e1xzmg0z.c1ofrhif.typo-10.mb-6.space-y-4.p-6.lg\\:space-y-8'
```

**Solution**: Fix escaped characters in CSS selectors

---

### 4. **Regex Pattern Errors**

**Error**: `re.error: bad escape sequence`
```python
# BROKEN - Double escaped
rating_match = re.search(r'(\\d+(?:\\.\\d+)?)', rating_text)

# FIXED - Single escaped
rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
```

**Solution**: Use proper regex escaping

---

### 5. **Windows Event Loop Errors**

**Error**: `NotImplementedError: asyncio subprocess on Windows is not supported`
```python
# Solution: Implement fallback scraping
def _fallback_scraping(self, company_name: str, capterra_url: str = None, max_reviews: int = 50):
    """Fallback scraping using requests if Playwright fails"""
    import requests
    from bs4 import BeautifulSoup
    # ... implementation
```

---

### 6. **Async/Await Issues**

**Error**: API returning 0 reviews despite successful scraping
```python
# BROKEN - Not awaiting
reviews = scraper.scrape_capterra_reviews_async(company, capterra_url, 10)

# FIXED - Proper await
reviews = await scraper.scrape_capterra_reviews_async(company, capterra_url, 10)
```

**Solution**: Always use `await` with async functions

---

### 7. **Sentiment Analysis Key Errors**

**Error**: `KeyError: 'compound'`
```python
# BROKEN - Wrong key
review['sentiment_score'] = sentiment['compound']

# FIXED - Correct key
review['sentiment_score'] = sentiment['sentiment_score']
```

**Solution**: Match VADER output keys correctly

---

### 8. **React Rendering Errors**

**Error**: `Objects are not valid as a React child`
```javascript
// BROKEN - Rendering objects
{realData?.platforms?.capterra}

// FIXED - Extract values
{typeof realData?.platforms?.capterra === 'object' 
  ? realData.platforms.capterra.reviews 
  : realData?.platforms?.capterra}
```

**Solution**: Transform objects to simple values before rendering

---

### 9. **File Path Issues**

**Error**: `FileNotFoundError: [Errno 2] No such file or directory`
```python
# BROKEN - Wrong path
csv_path = "company_review_urls.csv"

# FIXED - Absolute path
csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "company_review_urls.csv")
```

**Solution**: Use absolute paths or proper relative paths

---

### 10. **Port Already in Use**

**Error**: `Address already in use`
```bash
# Solution: Find and kill process
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

---

## 🔍 Debugging Techniques

### 1. **Backend Debugging**

**Add Debug Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"🔍 Debug: {variable}")
print(f"📊 Data: {data}")
```

**Test Individual Components**:
```python
# Test scraper directly
python quick_test.py

# Test API endpoint
curl -X POST http://localhost:8000/api/scrape/test-sage
```

### 2. **Frontend Debugging**

**Browser Console**:
```javascript
console.log("🔍 Debug:", data)
console.error("❌ Error:", error)
```

**Network Tab**: Check API calls and responses

### 3. **Data Validation**

**Validate Backend Response**:
```python
# Check response structure
print(f"Response keys: {data.keys()}")
print(f"Company results: {data.get('companyResults', [])}")
```

**Validate Frontend Data**:
```javascript
// Check data structure
console.log("Data structure:", JSON.stringify(data, null, 2))
```

---

## 🛠️ Development Tools

### 1. **Backend Testing**

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Test Scraping**:
```bash
curl -X POST http://localhost:8000/api/scrape/test-sage
```

**Test Live Scraping**:
```bash
curl -X POST http://localhost:8000/api/scrape/live \
  -H "Content-Type: application/json" \
  -d '{"companies": ["Sage"]}'
```

### 2. **Frontend Testing**

**Check if Running**:
```bash
curl http://localhost:3000
```

**Test API Proxy**:
```bash
curl -X POST http://localhost:3000/api/scrape/live \
  -H "Content-Type: application/json" \
  -d '{"companies": ["Sage"]}'
```

### 3. **Database Testing**

**Test Supabase Connection**:
```python
from utils.supabase_client import supabase

# Test connection
result = supabase.table("sentiment_data").select("*").limit(1).execute()
print(f"Connection test: {result}")
```

---

## 📋 Common Commands

### **Backend Commands**:
```bash
# Start backend
cd backend
python main.py

# Test scraping
python quick_test.py

# Test API
python test_api_flow.py
```

### **Frontend Commands**:
```bash
# Start frontend
cd frontend
npm run dev

# Install dependencies
npm install

# Build for production
npm run build
```

### **Git Commands**:
```bash
# Check status
git status

# Add changes
git add -A

# Commit
git commit -m "Description"

# Push
git push origin main
```

---

## 🎯 Performance Optimization

### 1. **Scraping Performance**

**Use Headless Mode**:
```python
browser = await p.chromium.launch(headless=True)
```

**Add Delays**:
```python
await asyncio.sleep(2)  # Between requests
```

**Limit Concurrent Requests**:
```python
# Process companies sequentially
for company in companies:
    await scrape_company(company)
    await asyncio.sleep(1)
```

### 2. **Frontend Performance**

**Optimize Re-renders**:
```javascript
// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }) => {
  // Component logic
})
```

**Debounce API Calls**:
```javascript
const debouncedScrape = useCallback(
  debounce(() => handleTestScraping(), 500),
  []
)
```

---

## 🚨 Emergency Procedures

### 1. **Backend Won't Start**

**Check Dependencies**:
```bash
pip install -r requirements.txt
```

**Check Port**:
```bash
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

**Check Python Version**:
```bash
python --version
```

### 2. **Frontend Won't Start**

**Clear Cache**:
```bash
rm -rf .next
npm run dev
```

**Reinstall Dependencies**:
```bash
rm -rf node_modules
npm install
```

**Check Node Version**:
```bash
node --version
```

### 3. **Scraping Not Working**

**Test Individual Components**:
```bash
python quick_test.py
```

**Check URLs**:
```bash
# Verify URLs in CSV
cat company_review_urls.csv
```

**Test with Different Browser**:
```python
# Try different browser
browser = await p.firefox.launch(headless=True)
```

---

## 📞 Support Resources

### **Documentation**:
- [Playwright Documentation](https://playwright.dev/python/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment)

### **Community**:
- [Stack Overflow](https://stackoverflow.com/)
- [GitHub Issues](https://github.com/FNLFLSH/Competitive-Intelligence/issues)

### **Debugging Tools**:
- Browser DevTools
- Postman for API testing
- Python debugger (pdb)
- React Developer Tools

---

*Last updated: July 17, 2025* 