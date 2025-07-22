# AI Screening Setup Guide

## Overview
The AI Screening tab now includes a ChatGPT-powered assistant that can analyze company review data from scraped sources (G2, Glassdoor, Capterra).

## Features

### 🤖 AI Assistant Capabilities
- **Sentiment Analysis**: Analyze sentiment scores and trends
- **Rating Analysis**: Compare average ratings across companies
- **Complaint Analysis**: Identify common user complaints and issues
- **Company Comparison**: Compare multiple companies side-by-side
- **Review Insights**: Extract insights from review data

### 💬 Chat Interface
- Real-time chat with AI assistant
- Suggested questions for quick analysis
- Company selector for focused analysis
- Quick stats sidebar with key metrics
- Message history with metadata

### 📊 Data Integration
- Connects to scraped review data from backend
- Analyzes sentiment scores and ratings
- Processes company-specific data
- Provides contextual responses

## Setup Instructions

### 1. Environment Configuration
Create a `.env.local` file in the frontend directory:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### 2. OpenAI API Key
1. Sign up for OpenAI API access at https://platform.openai.com
2. Generate an API key in your OpenAI dashboard
3. Add the key to your `.env.local` file

### 3. Backend Integration
The AI Screening feature works with the existing backend scraping functionality:
- Run scraping operations to collect review data
- The AI assistant will analyze the scraped data
- No additional backend setup required

## Usage

### Basic Usage
1. Navigate to the "AI Screening" tab
2. Select a company from the dropdown (if data is available)
3. Ask questions about the company's reviews and sentiment
4. Use suggested questions for quick analysis

### Example Questions
- "What's the general sentiment about Sage this week?"
- "Are users complaining about Sage's UX?"
- "What's the average rating for Sage?"
- "Show me recent reviews for Sage"
- "What are the most common complaints about Sage?"
- "Compare the companies in the dataset"

### Advanced Features
- **Company Selection**: Choose specific companies to analyze
- **Quick Stats**: View key metrics in the sidebar
- **Metadata Display**: See sentiment scores and ratings in responses
- **Comparison Mode**: Compare multiple companies

## Technical Implementation

### Frontend Components
- `AIScreeningChat`: Main chat interface component
- Real-time message handling
- Company data integration
- Suggested questions system

### API Endpoints
- `/api/chat/ai-screening`: Main AI analysis endpoint
- OpenAI API integration with fallback
- Context-aware responses
- Metadata extraction

### Data Flow
1. User sends message to AI assistant
2. Frontend calls `/api/chat/ai-screening`
3. API processes message with scraped data context
4. OpenAI API generates response (or fallback to mock)
5. Response displayed with metadata

## Fallback Mode
If no OpenAI API key is configured, the system uses a mock implementation that:
- Provides intelligent responses based on available data
- Analyzes sentiment scores and ratings
- Identifies common patterns in the data
- Offers helpful insights without external API calls

## Troubleshooting

### Common Issues
1. **No API Key**: System will use mock implementation
2. **No Scraped Data**: Assistant will prompt to run scraping first
3. **API Errors**: Automatic fallback to mock responses
4. **Company Not Found**: Assistant will list available companies

### Debug Steps
1. Check browser console for API errors
2. Verify OpenAI API key is set correctly
3. Ensure scraping has been run to collect data
4. Check network tab for API call status

## Future Enhancements
- Real-time data updates
- Advanced sentiment analysis
- Custom analysis templates
- Export functionality
- Integration with more data sources

## Security Notes
- API keys are stored server-side only
- No sensitive data is exposed to the frontend
- All API calls are proxied through Next.js API routes
- Fallback mode ensures functionality without external dependencies 