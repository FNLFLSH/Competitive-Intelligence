# Craig Intelligence Dashboard

## Setup Instructions

1. **Install Dependencies**
   \`\`\`bash
   npm install
   \`\`\`

2. **Environment Variables**
   \`\`\`bash
   cp .env.local.example .env.local
   # Edit .env.local with your actual values
   \`\`\`

3. **Start Development Server**
   \`\`\`bash
   npm run dev
   \`\`\`

4. **Open Browser**
   Navigate to http://localhost:3000

## Features
- Live sentiment scraping
- Company intelligence dashboard
- AI-powered chat widget
- Real-time data visualization

## API Endpoints
- `/api/scrape/live` - Live scraping with sentiment analysis
- `/api/scrape/test-sentiment` - Test sentiment analysis
- `/api/chat` - AI chat functionality
