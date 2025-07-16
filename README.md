# Intelligence Backend

A comprehensive backend system for scraping reviews from G2 and Glassdoor, performing sentiment analysis, and providing a FastAPI-based API.

## Project Structure

```
INTELLIGENCE_BACKEND/
├── backend/                    # Main backend application
│   ├── integrated_review_scraper.py
│   ├── requirements.txt
│   ├── SETUP_GUIDE.md
│   ├── utils/
│   │   ├── supabase_client.py
│   │   └── ai_keywords.py
│   └── README.md
├── frontend/                   # Frontend integration files
│   └── README.md
├── test_*.py                  # Test scripts
├── Competitor Master List (4).csv
└── README.md                  # This file
```

## Quick Start

1. **Navigate to Backend**:
   ```bash
   cd backend
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Backend**:
   ```bash
   python integrated_review_scraper.py
   ```

4. **Test the API**:
   ```bash
   # From the root directory
   python test_api.py
   ```

## Features

- **Review Scraping**: G2 and Glassdoor review extraction
- **Sentiment Analysis**: VADER-based sentiment scoring
- **Supabase Integration**: Cloud database storage
- **FastAPI Backend**: RESTful API endpoints
- **Frontend Integration**: Compatible with v0 frontend

## Documentation

- [Backend Documentation](backend/README.md) - Backend-specific documentation
- [Frontend Integration](frontend/README.md) - Frontend integration guide
- [Setup Guide](backend/SETUP_GUIDE.md) - Detailed setup instructions

## Testing

Run test scripts from the root directory:
- `test_api.py` - API endpoint testing
- `test_proxy_setup.py` - Proxy configuration testing
- `test_complete_workflow.py` - End-to-end workflow testing

## Architecture

```
Frontend (v0) ←→ Backend (FastAPI) ←→ Supabase
     ↓              ↓                    ↓
   React App    Review Scraper      Data Storage
   Proxy Setup  Sentiment Analysis  Sentiment Results
```