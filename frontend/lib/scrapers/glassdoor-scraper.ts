import puppeteer from 'puppeteer';

export interface GlassdoorReview {
  id: string;
  title: string;
  content: string;
  rating: number;
  author: string;
  date: string;
  pros?: string;
  cons?: string;
  helpful: number;
  verified: boolean;
  reviewType: 'pros' | 'cons' | 'advice' | 'overall';
}

export interface GlassdoorScrapingResult {
  company: string;
  url: string;
  reviews: GlassdoorReview[];
  totalReviews: number;
  averageRating: number;
  success: boolean;
  error?: string;
}

export class GlassdoorScraper {
  private browser: puppeteer.Browser | null = null;

  async initialize() {
    if (!this.browser) {
      this.browser = await puppeteer.launch({
        headless: true,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--no-first-run',
          '--no-zygote',
          '--disable-gpu'
        ]
      });
    }
  }

  async scrapeReviews(companyName: string, glassdoorUrl: string): Promise<GlassdoorScrapingResult> {
    try {
      await this.initialize();
      const page = await this.browser!.newPage();
      
      // Set user agent to avoid detection
      await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
      
      // Navigate to the Glassdoor reviews page
      await page.goto(glassdoorUrl, { waitUntil: 'networkidle2', timeout: 30000 });
      
      // Wait for reviews to load
      await page.waitForSelector('.review', { timeout: 10000 });
      
      // Extract review data
      const reviews = await page.evaluate(() => {
        const reviewElements = document.querySelectorAll('.review');
        const reviews: GlassdoorReview[] = [];
        
        reviewElements.forEach((element, index) => {
          try {
            const reviewId = element.getAttribute('data-review-id') || `review-${index}`;
            const titleElement = element.querySelector('.review-title');
            const contentElement = element.querySelector('.review-content');
            const ratingElement = element.querySelector('.rating');
            const authorElement = element.querySelector('.reviewer-name');
            const dateElement = element.querySelector('.review-date');
            const prosElement = element.querySelector('.pros');
            const consElement = element.querySelector('.cons');
            const helpfulElement = element.querySelector('.helpful-count');
            const verifiedElement = element.querySelector('.verified-badge');
            const reviewTypeElement = element.querySelector('.review-type');
            
            const title = titleElement?.textContent?.trim() || '';
            const content = contentElement?.textContent?.trim() || '';
            const rating = ratingElement ? parseFloat(ratingElement.getAttribute('aria-label')?.match(/\d+/)?.[0] || '0') : 0;
            const author = authorElement?.textContent?.trim() || 'Anonymous';
            const date = dateElement?.textContent?.trim() || '';
            const pros = prosElement?.textContent?.trim() || '';
            const cons = consElement?.textContent?.trim() || '';
            const helpful = helpfulElement ? parseInt(helpfulElement.textContent?.match(/\d+/)?.[0] || '0') : 0;
            const verified = !!verifiedElement;
            const reviewType = (reviewTypeElement?.textContent?.trim() || 'overall') as 'pros' | 'cons' | 'advice' | 'overall';
            
            reviews.push({
              id: reviewId,
              title,
              content,
              rating,
              author,
              date,
              pros,
              cons,
              helpful,
              verified,
              reviewType
            });
          } catch (error) {
            console.error('Error parsing review element:', error);
          }
        });
        
        return reviews;
      });
      
      // Calculate statistics
      const totalReviews = reviews.length;
      const averageRating = reviews.length > 0 
        ? reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length 
        : 0;
      
      await page.close();
      
      return {
        company: companyName,
        url: glassdoorUrl,
        reviews,
        totalReviews,
        averageRating,
        success: true
      };
      
    } catch (error) {
      console.error(`Error scraping Glassdoor reviews for ${companyName}:`, error);
      return {
        company: companyName,
        url: glassdoorUrl,
        reviews: [],
        totalReviews: 0,
        averageRating: 0,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }
}
