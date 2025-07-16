# Review Scraper Backend

This backend provides a FastAPI-based API for scraping reviews from G2 and Glassdoor, performing sentiment analysis, and storing results in Supabase.

## Project Structure

```
backend/
├── integrated_review_scraper.py  # Main FastAPI application
├── requirements.txt              # Python dependencies
├── SETUP_GUIDE.md              # Detailed setup instructions
├── utils/
│   ├── supabase_client.py      # Supabase connection utilities
│   └── ai_keywords.py          # AI keyword utilities
└── README.md                   # This file
```

## Features

- **Live Scraping**: Real-time scraping of G2 and Glassdoor reviews
- **Sentiment Analysis**: VADER sentiment analysis for scraped reviews
- **Supabase Integration**: Automatic storage of scraped data and sentiment results
- **FastAPI Endpoints**: RESTful API compatible with v0 frontend
- **Proxy Support**: Can be accessed through frontend proxy

## API Endpoints

- `POST /api/scrape/live` - Live scraping of reviews
- `POST /api/scrape/live-sentiment` - Live scraping with sentiment analysis
- `GET /api/scrape/live-sentiment` - Retrieve sentiment analysis results
- `POST /api/chat` - Chat endpoint for AI interactions
- `GET /health` - Health check endpoint

## Quick Start

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase API key

3. **Run the Backend**:
   ```bash
   python integrated_review_scraper.py
   ```

4. **Access the API**:
   - API will be available at: http://localhost:8000
   - Health check: http://localhost:8000/health

## Configuration

The backend is configured to work with:
- **Supabase**: For data storage and retrieval
- **VADER Sentiment Analysis**: For review sentiment scoring
- **Selenium WebDriver**: For web scraping
- **FastAPI**: For API endpoints

## Integration with Frontend

The backend is designed to work with the v0 frontend through:
- Direct API calls
- Proxy forwarding
- Environment variable configuration

See `SETUP_GUIDE.md` for detailed integration instructions.

## Testing

Test scripts are available in the root directory:
- `test_api.py` - API endpoint testing
- `test_proxy_setup.py` - Proxy configuration testing
- `test_complete_workflow.py` - End-to-end workflow testing

## Troubleshooting

1. **Missing Dependencies**: Run `pip install -r requirements.txt`
2. **Supabase Connection**: Verify environment variables are set correctly
3. **Scraping Issues**: Check browser driver installation and proxy settings
4. **API Errors**: Check logs for detailed error messages

For detailed setup instructions, see `SETUP_GUIDE.md`. 