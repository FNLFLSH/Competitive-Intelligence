import puppeteer from 'puppeteer';

export interface G2Review {
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
}

export interface G2ScrapingResult {
  company: string;
  url: string;
  reviews: G2Review[];
  totalReviews: number;
  averageRating: number;
  success: boolean;
  error?: string;
}

export class G2Scraper {
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

  async scrapeReviews(companyName: string, g2Url: string): Promise<G2ScrapingResult> {
    try {
      await this.initialize();
      const page = await this.browser!.newPage();
      
      // Set user agent to avoid detection
      await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
      
      // Navigate to the G2 reviews page
      await page.goto(g2Url, { waitUntil: 'networkidle2', timeout: 30000 });
      
      // Wait for reviews to load
      await page.waitForSelector('[data-testid="review-item"]', { timeout: 10000 });
      
      // Extract review data
      const reviews = await page.evaluate(() => {
        const reviewElements = document.querySelectorAll('[data-testid="review-item"]');
        const reviews: G2Review[] = [];
        
        reviewElements.forEach((element, index) => {
          try {
            const reviewId = element.getAttribute('data-review-id') || `review-${index}`;
            const titleElement = element.querySelector('[data-testid="review-title"]');
            const contentElement = element.querySelector('[data-testid="review-content"]');
            const ratingElement = element.querySelector('[data-testid="rating"]');
            const authorElement = element.querySelector('[data-testid="reviewer-name"]');
            const dateElement = element.querySelector('[data-testid="review-date"]');
            const prosElement = element.querySelector('[data-testid="pros"]');
            const consElement = element.querySelector('[data-testid="cons"]');
            const helpfulElement = element.querySelector('[data-testid="helpful-count"]');
            const verifiedElement = element.querySelector('[data-testid="verified-badge"]');
            
            const title = titleElement?.textContent?.trim() || '';
            const content = contentElement?.textContent?.trim() || '';
            const rating = ratingElement ? parseFloat(ratingElement.getAttribute('aria-label')?.match(/\d+/)?.[0] || '0') : 0;
            const author = authorElement?.textContent?.trim() || 'Anonymous';
            const date = dateElement?.textContent?.trim() || '';
            const pros = prosElement?.textContent?.trim() || '';
            const cons = consElement?.textContent?.trim() || '';
            const helpful = helpfulElement ? parseInt(helpfulElement.textContent?.match(/\d+/)?.[0] || '0') : 0;
            const verified = !!verifiedElement;
            
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
              verified
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
        url: g2Url,
        reviews,
        totalReviews,
        averageRating,
        success: true
      };
      
    } catch (error) {
      console.error(`Error scraping G2 reviews for ${companyName}:`, error);
      return {
        company: companyName,
        url: g2Url,
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
