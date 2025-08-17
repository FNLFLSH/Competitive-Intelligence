import { BaseScraper, type ScrapedData, type Review } from "./base-scraper"

export class LinkedInScraper extends BaseScraper {
  private accessToken: string

  constructor() {
    super("linkedin", "https://api.linkedin.com/v2")
    this.accessToken = process.env.LINKEDIN_ACCESS_TOKEN || ""
  }

  async scrapeCompany(companyName: string): Promise<ScrapedData> {
    if (!this.accessToken) {
      throw new Error("LinkedIn access token not configured")
    }

    try {
      // First, search for the company
      const companySearchUrl = `${this.baseUrl}/companySearch?q=${encodeURIComponent(companyName)}`

      const companyResponse = await this.fetchWithRetry(companySearchUrl, {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
          "X-Restli-Protocol-Version": "2.0.0",
        },
      })

      const companyData = await companyResponse.json()

      if (!companyData.elements || companyData.elements.length === 0) {
        return this.createEmptyResult(companyName)
      }

      const companyId = companyData.elements[0].id

      // Get company updates/posts
      const updatesUrl = `${this.baseUrl}/shares?q=owners&owners=urn:li:organization:${companyId}&count=50`

      const updatesResponse = await this.fetchWithRetry(updatesUrl, {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
          "X-Restli-Protocol-Version": "2.0.0",
        },
      })

      const updatesData = await updatesResponse.json()

      const reviews: Review[] = (updatesData.elements || []).map((update: any) => ({
        id: this.generateReviewId(companyName, update.text?.text || ""),
        content: this.sanitizeText(update.text?.text || ""),
        date: new Date(update.created?.time || Date.now()),
      }))

      return {
        platform: this.platform,
        company: companyName,
        reviews,
        metadata: {
          totalReviews: reviews.length,
          averageRating: 0,
          scrapedAt: new Date(),
          url: `https://linkedin.com/company/${companyName.toLowerCase().replace(/\s+/g, "-")}`,
        },
      }
    } catch (error) {
      console.error(`LinkedIn scraping failed for ${companyName}:`, error)
      return this.createEmptyResult(companyName)
    }
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
