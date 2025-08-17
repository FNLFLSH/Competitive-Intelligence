import { BaseScraper, type ScrapedData, type Review } from "./base-scraper"

export class RedditScraper extends BaseScraper {
  private clientId: string
  private clientSecret: string
  private userAgent: string

  constructor() {
    super("reddit", "https://oauth.reddit.com")
    this.clientId = process.env.REDDIT_CLIENT_ID || ""
    this.clientSecret = process.env.REDDIT_CLIENT_SECRET || ""
    this.userAgent = "CompetitiveIntelligence/1.0"
  }

  async scrapeCompany(companyName: string): Promise<ScrapedData> {
    if (!this.clientId || !this.clientSecret) {
      throw new Error("Reddit API credentials not configured")
    }

    try {
      const accessToken = await this.getAccessToken()
      const query = `${companyName} subreddit:accounting OR subreddit:smallbusiness OR subreddit:entrepreneur`

      const searchUrl = `${this.baseUrl}/search?q=${encodeURIComponent(query)}&sort=relevance&limit=100&type=link,comment`

      const response = await this.fetchWithRetry(searchUrl, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          "User-Agent": this.userAgent,
        },
      })

      const data = await response.json()

      if (!data.data || !data.data.children) {
        return this.createEmptyResult(companyName)
      }

      const reviews: Review[] = data.data.children
        .filter((item: any) => item.data.selftext || item.data.body)
        .map((item: any) => ({
          id: this.generateReviewId(companyName, item.data.selftext || item.data.body),
          title: item.data.title,
          content: this.sanitizeText(item.data.selftext || item.data.body || ""),
          author: item.data.author,
          date: new Date(item.data.created_utc * 1000),
          rating: item.data.score,
        }))

      return {
        platform: this.platform,
        company: companyName,
        reviews,
        metadata: {
          totalReviews: reviews.length,
          averageRating: reviews.reduce((sum, r) => sum + (r.rating || 0), 0) / reviews.length,
          scrapedAt: new Date(),
        },
      }
    } catch (error) {
      console.error(`Reddit scraping failed for ${companyName}:`, error)
      return this.createEmptyResult(companyName)
    }
  }

  private async getAccessToken(): Promise<string> {
    const auth = Buffer.from(`${this.clientId}:${this.clientSecret}`).toString("base64")

    const response = await fetch("https://www.reddit.com/api/v1/access_token", {
      method: "POST",
      headers: {
        Authorization: `Basic ${auth}`,
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": this.userAgent,
      },
      body: "grant_type=client_credentials",
    })

    const data = await response.json()
    return data.access_token
  }

  private createEmptyResult(companyName: string): ScrapedData {
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
