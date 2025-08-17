import { BaseScraper, type ScrapedData, type Review } from "./base-scraper"

export class TwitterScraper extends BaseScraper {
  private apiKey: string

  constructor() {
    super("twitter", "https://api.twitter.com/2")
    this.apiKey = process.env.TWITTER_API_KEY || ""
  }

  async scrapeCompany(companyName: string): Promise<ScrapedData> {
    if (!this.apiKey) {
      throw new Error("Twitter API key not configured")
    }

    try {
      const query = `${companyName} -is:retweet lang:en`
      const url = `${this.baseUrl}/tweets/search/recent?query=${encodeURIComponent(query)}&max_results=100&tweet.fields=created_at,author_id,public_metrics,context_annotations`

      const response = await this.fetchWithRetry(url, {
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
        },
      })

      const data = await response.json()

      if (!data.data) {
        return {
          platform: this.platform,
          company: companyName,
          reviews: [],
          metadata: {
            totalReviews: 0,
            averageRating: 0,
            scrapedAt: new Date(),
          },
        }
      }

      const reviews: Review[] = data.data.map((tweet: any) => ({
        id: this.generateReviewId(companyName, tweet.text),
        content: this.sanitizeText(tweet.text),
        author: tweet.author_id,
        date: new Date(tweet.created_at),
      }))

      return {
        platform: this.platform,
        company: companyName,
        reviews,
        metadata: {
          totalReviews: reviews.length,
          averageRating: 0, // Twitter doesn't have ratings
          scrapedAt: new Date(),
        },
      }
    } catch (error) {
      console.error(`Twitter scraping failed for ${companyName}:`, error)
      return {
        platform: this.platform,
        company: companyName,
        reviews: [],
        metadata: {
          totalReviews: 0,
          averageRating: 0,
          scrapedAt: new Date(),
        },
      }
    }
  }
}
