# Review Scraping System Setup Instructions

This system provides comprehensive scraping of G2 and Glassdoor reviews with VADER sentiment analysis, storing results in Supabase.

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env.local` file in the frontend directory:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Optional: Backend URL (if using separate backend)
SCRAPER_BACKEND_URL=http://localhost:8000
```

### 2. Database Setup

Run the SQL schema in your Supabase SQL editor:

```sql
-- Copy and paste the contents of supabase-schema.sql
```

### 3. Install Dependencies

```bash
cd frontend
npm install
# or
pnpm install
```

### 4. Start Development Server

```bash
npm run dev
# or
pnpm dev
```

## 📁 File Structure

```
frontend/
├── lib/
│   ├── scrapers/
│   │   ├── g2-scraper.ts          # G2 review scraper
│   │   ├── glassdoor-scraper.ts   # Glassdoor review scraper
│   │   └── review-scraper-manager.ts # Main scraping coordinator
│   └── sentiment/
│       └── vader-sentiment.ts     # VADER sentiment analysis
├── app/api/scrape/
│   └── live-sentiment/
│       └── route.ts               # API endpoint for live scraping
├── components/
│   └── live-sentiment-scraper.tsx # React component for UI
└── company_review_urls.csv        # Company URLs data
```

## 🔧 Configuration

### Supabase Tables

The system creates these tables:

1. **`company_sentiment_summary`** - Overall sentiment scores per company
2. **`company_reviews`** - Individual reviews with sentiment analysis
3. **`scraping_sessions`** - Track scraping runs
4. **`company_urls`** - Store known company URLs
5. **`sentiment_cache`** - Cache sentiment analysis results

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL | Yes |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anonymous key | Yes |
| `SCRAPER_BACKEND_URL` | Backend server URL (if separate) | No |

## 🎯 Usage

### 1. Load Company Data

The system automatically loads companies from `company_review_urls.csv`:

```csv
Company,G2_URL,Glassdoor_URL
Access Group,https://www.g2.com/products/access-peoplehr/reviews#reviews,https://www.glassdoor.com/Reviews/The-Access-Group-UK-Reviews-E913550.htm
```

### 2. Live Scraping

1. Navigate to the Live Sentiment Scraper component
2. Select companies from the list
3. Click "Live Scrape" to start scraping
4. Monitor progress and view results

### 3. API Endpoint

POST `/api/scrape/live-sentiment`

```json
{
  "companies": [
    {
      "name": "Access Group",
      "g2Url": "https://www.g2.com/products/access-peoplehr/reviews#reviews",
      "glassdoorUrl": "https://www.glassdoor.com/Reviews/The-Access-Group-UK-Reviews-E913550.htm"
    }
  ]
}
```

## 📊 Sentiment Analysis

### VADER Scoring

The system uses VADER (Valence Aware Dictionary and sEntiment Reasoner) with a custom scale:

- **Score Range**: -4 to +4
- **Labels**:
  - +3 to +4: Very Positive
  - +1 to +2: Positive
  - -1 to +1: Neutral
  - -2 to -1: Negative
  - -4 to -3: Very Negative

### Features Analyzed

- **Content**: Main review text
- **Pros**: Positive aspects (Glassdoor)
- **Cons**: Negative aspects (Glassdoor)
- **Rating**: Numerical rating (1-5 stars)
- **Helpful**: Number of helpful votes
- **Verified**: Whether review is verified

## 🔍 Scraping Features

### G2 Scraper
- Extracts review content, ratings, and metadata
- Handles pagination and dynamic loading
- Respects rate limits and user agents

### Glassdoor Scraper
- Scrapes company review pages
- Extracts pros, cons, and advice sections
- Handles different review types

### Error Handling
- Graceful failure for individual companies
- Continues scraping even if some fail
- Detailed error logging

## 📈 Data Storage

### Company Sentiment Summary
```sql
SELECT * FROM company_sentiment_summary 
WHERE company = 'Access Group' 
ORDER BY scraped_at DESC;
```

### Individual Reviews
```sql
SELECT * FROM company_reviews 
WHERE company = 'Access Group' 
AND platform = 'g2'
ORDER BY scraped_at DESC;
```

### Sentiment Trends
```sql
SELECT * FROM get_sentiment_trends('Access Group', 90);
```

## 🛠️ Customization

### Adding New Companies

1. Add to `company_review_urls.csv`:
```csv
New Company,https://g2-url,https://glassdoor-url
```

2. Or insert into database:
```sql
INSERT INTO company_urls (company, g2_url, glassdoor_url) 
VALUES ('New Company', 'https://g2-url', 'https://glassdoor-url');
```

### Modifying Sentiment Analysis

Edit `lib/sentiment/vader-sentiment.ts`:
- Add new words to `VADER_LEXICON`
- Modify scoring algorithms
- Add custom sentiment rules

### Custom Scraping Logic

Modify scrapers in `lib/scrapers/`:
- Update selectors for website changes
- Add new data extraction fields
- Implement custom error handling

## 🚨 Important Notes

### Rate Limiting
- Built-in delays between requests
- Respects website terms of service
- Use responsibly and ethically

### Legal Considerations
- Ensure compliance with website terms
- Respect robots.txt files
- Consider data privacy regulations

### Performance
- Scraping can take several minutes for multiple companies
- Consider running during off-peak hours
- Monitor server resources

## 🔧 Troubleshooting

### Common Issues

1. **Puppeteer Installation**
   ```bash
   # On Linux, you might need:
   sudo apt-get install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
   ```

2. **Supabase Connection**
   - Verify environment variables
   - Check RLS policies
   - Ensure tables exist

3. **Scraping Failures**
   - Check website structure changes
   - Verify URLs are accessible
   - Review error logs

### Debug Mode

Enable detailed logging:
```typescript
// In scrapers, add:
console.log('Scraping details:', { url, company });
```

## 📚 API Reference

### ReviewScraperManager

```typescript
const manager = new ReviewScraperManager();

// Scrape single company
const result = await manager.scrapeCompanyReviews(
  'Company Name',
  'g2-url',
  'glassdoor-url'
);

// Scrape multiple companies
const results = await manager.scrapeMultipleCompanies([
  { name: 'Company 1', g2Url: 'url1', glassdoorUrl: 'url2' }
]);

// Save to database
await manager.saveToSupabase(companyData);
```

### Sentiment Analysis

```typescript
import { analyzeVaderSentiment, getSentimentLabel } from '@/lib/sentiment/vader-sentiment';

const sentiment = analyzeVaderSentiment('This product is amazing!');
console.log(sentiment.score); // -4 to +4
console.log(getSentimentLabel(sentiment.score)); // "Very Positive"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational and research purposes. Please respect website terms of service and use responsibly. 