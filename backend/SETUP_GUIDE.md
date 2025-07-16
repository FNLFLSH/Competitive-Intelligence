# 🚀 Integrated Review Scraper Setup Guide

This guide will help you set up the integrated review scraper with your Supabase database.

## 📋 Prerequisites

- Python 3.8+
- Chrome browser installed
- Supabase account with your project URL and API key

## 🔧 Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## 🗄️ Step 2: Set Up Supabase Database

### Option A: Using SQL Script (Recommended)

1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/woulqutyrdzymmhooujj
2. Navigate to the SQL Editor
3. Copy and paste the contents of `create_sentiment_table.sql`
4. Run the SQL script

### Option B: Manual Table Creation

If you prefer to create the table manually:

1. Go to your Supabase dashboard
2. Navigate to Table Editor
3. Create a new table called `sentiment_data` with these columns:

| Column Name | Type | Default | Notes |
|-------------|------|---------|-------|
| id | BIGSERIAL | PRIMARY KEY | Auto-incrementing ID |
| company_name | TEXT | NOT NULL | Company name |
| source | TEXT | NOT NULL | Source (g2, glassdoor, etc.) |
| review_text | TEXT | NOT NULL | Full review text |
| rating | DECIMAL(3,2) | NULL | Review rating (0-5) |
| reviewer_name | TEXT | '' | Reviewer name |
| reviewer_title | TEXT | '' | Reviewer job title |
| reviewer_company | TEXT | '' | Reviewer's company |
| reviewer_location | TEXT | '' | Reviewer location |
| review_date | TEXT | '' | Review date |
| pros | TEXT | '' | Pros from review |
| cons | TEXT | '' | Cons from review |
| sentiment_compound | DECIMAL(4,3) | NULL | VADER compound sentiment |
| sentiment_positive | DECIMAL(4,3) | NULL | VADER positive sentiment |
| sentiment_negative | DECIMAL(4,3) | NULL | VADER negative sentiment |
| sentiment_neutral | DECIMAL(4,3) | NULL | VADER neutral sentiment |
| scraped_at | TIMESTAMP | NOW() | When review was scraped |
| created_at | TIMESTAMP | NOW() | Record creation time |

## ✅ Step 3: Verify Setup

Run the setup verification script:

```bash
python setup_sentiment_table.py
```

You should see:
```
✅ sentiment_data table exists
✅ Table schema is correct and ready for data
✅ Test data cleaned up
✅ Setup complete! Your sentiment_data table is ready for scraping.
```

## 🚀 Step 4: Start the API Server

```bash
python integrated_review_scraper.py
```

The server will start on `http://localhost:8000`

## 🧪 Step 5: Test the API

Run the API test script:

```bash
python test_api.py
```

## 📊 Available API Endpoints

### Health Check
```
GET /health
```

### Start Scraping
```
POST /scrape
Content-Type: application/json

{
  "company_name": "Microsoft",
  "sources": ["g2", "glassdoor"],
  "max_reviews": 50,
  "headless": true
}
```

### Check Scraping Status
```
GET /status
```

### Get Reviews for Company
```
GET /reviews/{company_name}?source=g2
```

### Get All Companies
```
GET /companies
```

### Get Analytics
```
GET /analytics/{company_name}
```

## 🔍 Step 6: Test Scraping

### Test with a Single Company

```bash
curl -X POST "http://localhost:8000/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Microsoft",
    "sources": ["g2"],
    "max_reviews": 5,
    "headless": true
  }'
```

### Monitor Progress

```bash
curl "http://localhost:8000/status"
```

### Check Results

```bash
curl "http://localhost:8000/reviews/Microsoft"
```

## 🎯 Integration with Your Frontend

The API is designed to work with your existing v0 frontend. Here's how to integrate:

### 1. Update Your Frontend API Calls

Replace your existing API calls with the new endpoints:

```javascript
// Example: Start scraping
const startScraping = async (companyName) => {
  const response = await fetch('http://localhost:8000/scrape', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      company_name: companyName,
      sources: ['g2', 'glassdoor'],
      max_reviews: 50,
      headless: true
    })
  });
  return response.json();
};

// Example: Get reviews
const getReviews = async (companyName) => {
  const response = await fetch(`http://localhost:8000/reviews/${encodeURIComponent(companyName)}`);
  return response.json();
};

// Example: Get analytics
const getAnalytics = async (companyName) => {
  const response = await fetch(`http://localhost:8000/analytics/${encodeURIComponent(companyName)}`);
  return response.json();
};
```

### 2. Monitor Scraping Status

```javascript
const checkStatus = async () => {
  const response = await fetch('http://localhost:8000/status');
  return response.json();
};

// Poll status every 5 seconds
setInterval(async () => {
  const status = await checkStatus();
  if (status.status === 'completed') {
    // Update UI with results
    console.log('Scraping completed!');
  }
}, 5000);
```

## 🔧 Configuration

### Environment Variables

You can set these environment variables:

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key
- `API_HOST`: API server host (default: 0.0.0.0)
- `API_PORT`: API server port (default: 8000)

### Headless Mode

The scraper runs in headless mode by default. Set `headless: false` in your scraping request to see the browser window (useful for debugging).

## 🚨 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   ```bash
   # Kill existing Chrome processes
   taskkill /f /im chrome.exe
   taskkill /f /im chromedriver.exe
   ```

2. **Supabase Connection Issues**
   - Verify your URL and API key in `utils/supabase_client.py`
   - Check that your Supabase project is active

3. **Table Schema Issues**
   - Run the SQL script in Supabase SQL Editor
   - Verify table columns match the expected schema

4. **Scraping Fails**
   - Try with `headless: false` to see what's happening
   - Check if the target sites are accessible
   - Verify company names are correct

### Debug Mode

To run with debug output:

```python
# In integrated_review_scraper.py, change:
headless = False
```

## 📈 Monitoring and Analytics

The system provides:

- Real-time scraping status
- Review sentiment analysis
- Company analytics
- Progress tracking
- Error handling

## 🔒 Security Notes

- Keep your Supabase API key secure
- Consider implementing rate limiting
- Monitor scraping activity
- Respect website terms of service

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Verify your Supabase setup
3. Test with a simple company name first
4. Check the API logs for error messages

---

**Ready to start scraping! 🎉** 