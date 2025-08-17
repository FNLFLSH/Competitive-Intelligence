import type { ScrapedPost, ScrapedData } from "./base-scraper"
import { TwitterScraper } from "./twitter-scraper"
import { LinkedInScraper } from "./linkedin-scraper"
import { RedditScraper } from "./reddit-scraper"
import { G2Scraper } from "./g2-scraper"
import { YouTubeScraper } from "./youtube-scraper"
import { GlassdoorScraper } from "./glassdoor-scraper"
import { analyzeSentiment } from "../sentiment/sentiment-analyzer"

export interface ScraperCredentials {
  twitter?: {
    apiKey: string
    apiSecret: string
    bearerToken: string
  }
  reddit?: {
    clientId: string
    clientSecret: string
    userAgent: string
  }
  youtube?: {
    apiKey: string
  }
  linkedin?: {
    sessionCookie: string
  }
}

export interface ScrapingResult {
  success: boolean
  data: ScrapedData[]
  summary: {
    totalReviews: number
    companiesAnalyzed: number
    platformsUsed: string[]
    avgProcessingTime: string
    g2Reviews: number
    glassdoorReviews: number
  }
  platformBreakdown: {
    [platform: string]: {
      reviews: number
      avgSentiment: number
    }
  }
  companySentiments: {
    [company: string]: {
      totalReviews: number
      averageSentiment: number
      platforms: {
        [platform: string]: number
      }
    }
  }
  errors: string[]
}

export class ScraperManager {
  private scrapers: Map<string, any>
  private credentials: ScraperCredentials

  constructor(credentials: ScraperCredentials) {
    this.credentials = credentials
    this.scrapers = new Map([
      ["twitter", new TwitterScraper(credentials.twitter)],
      ["reddit", new RedditScraper(credentials.reddit)],
      ["g2", new G2Scraper()],
      ["youtube", new YouTubeScraper(credentials.youtube)],
      ["glassdoor", new GlassdoorScraper()],
      ["linkedin", new LinkedInScraper(credentials.linkedin)],
    ])
  }

  async scrapeAll(): Promise<Map<string, ScrapedPost[]>> {
    const results = new Map<string, ScrapedPost[]>()
    const promises: Promise<void>[] = []

    for (const [platform, scraper] of this.scrapers) {
      promises.push(
        scraper
          .scrape()
          .then((posts) => {
            results.set(platform, posts)
            console.log(`✅ Scraped ${posts.length} posts from ${platform}`)
          })
          .catch((error) => {
            console.error(`❌ Error scraping ${platform}:`, error)
            results.set(platform, [])
          }),
      )
    }

    await Promise.all(promises)
    return results
  }

  async scrapeSpecific(platforms: string[]): Promise<Map<string, ScrapedPost[]>> {
    const results = new Map<string, ScrapedPost[]>()
    const promises: Promise<void>[] = []

    for (const platform of platforms) {
      const scraper = this.scrapers.get(platform)
      if (scraper) {
        promises.push(
          scraper
            .scrape()
            .then((posts) => {
              results.set(platform, posts)
              console.log(`✅ Scraped ${posts.length} posts from ${platform}`)
            })
            .catch((error) => {
              console.error(`❌ Error scraping ${platform}:`, error)
              results.set(platform, [])
            }),
        )
      }
    }

    await Promise.all(promises)
    return results
  }

  // New method specifically for hiring intelligence
  async scrapeHiringData(): Promise<ScrapedPost[]> {
    const linkedinScraper = this.scrapers.get("linkedin")
    if (!linkedinScraper) {
      console.log("LinkedIn scraper not configured for hiring intelligence")
      return []
    }

    try {
      const hiringPosts = await linkedinScraper.scrape()
      console.log(`✅ Scraped ${hiringPosts.length} hiring posts from LinkedIn`)
      return hiringPosts
    } catch (error) {
      console.error("❌ Error scraping LinkedIn hiring data:", error)
      return []
    }
  }

  getAvailablePlatforms(): string[] {
    return Array.from(this.scrapers.keys())
  }

  getHiringPlatforms(): string[] {
    return this.scrapers.has("linkedin") ? ["linkedin"] : []
  }

  async scrapeCompanies(
    companies: string[],
    platforms: string[] = ["g2", "glassdoor"],
    options: { includeSentiment?: boolean } = {},
  ): Promise<ScrapingResult> {
    const startTime = Date.now()
    const results: ScrapedData[] = []
    const errors: string[] = []

    console.log(`🚀 Starting scraping for ${companies.length} companies across ${platforms.length} platforms`)

    for (const company of companies) {
      for (const platform of platforms) {
        const scraper = this.scrapers.get(platform)
        if (!scraper) {
          errors.push(`Unknown platform: ${platform}`)
          continue
        }

        try {
          console.log(`📊 Scraping ${company} from ${platform}...`)
          const data = await scraper.scrapeCompany(company)

          // Add sentiment analysis if requested
          if (options.includeSentiment && data.reviews.length > 0) {
            for (const review of data.reviews) {
              if (!review.sentiment) {
                review.sentiment = analyzeSentiment(review.content)
              }
            }
          }

          results.push(data)
          console.log(`✅ ${company} (${platform}): ${data.reviews.length} reviews`)
        } catch (error) {
          const errorMsg = `Failed to scrape ${company} from ${platform}: ${error}`
          errors.push(errorMsg)
          console.error(`❌ ${errorMsg}`)
        }

        // Rate limiting
        await this.delay(500)
      }
    }

    const endTime = Date.now()
    const processingTime = ((endTime - startTime) / 1000).toFixed(2)

    // Calculate summary statistics
    const summary = this.calculateSummary(results, processingTime)
    const platformBreakdown = this.calculatePlatformBreakdown(results)
    const companySentiments = this.calculateCompanySentiments(results)

    return {
      success: results.length > 0,
      data: results,
      summary,
      platformBreakdown,
      companySentiments,
      errors,
    }
  }

  private calculateSummary(results: ScrapedData[], processingTime: string) {
    const totalReviews = results.reduce((sum, r) => sum + r.reviews.length, 0)
    const companiesAnalyzed = new Set(results.map((r) => r.company)).size
    const platformsUsed = [...new Set(results.map((r) => r.platform))]
    const g2Reviews = results.filter((r) => r.platform === "g2").reduce((sum, r) => sum + r.reviews.length, 0)
    const glassdoorReviews = results
      .filter((r) => r.platform === "glassdoor")
      .reduce((sum, r) => sum + r.reviews.length, 0)

    return {
      totalReviews,
      companiesAnalyzed,
      platformsUsed,
      avgProcessingTime: `${processingTime}s`,
      g2Reviews,
      glassdoorReviews,
    }
  }

  private calculatePlatformBreakdown(results: ScrapedData[]) {
    const breakdown: { [platform: string]: { reviews: number; avgSentiment: number } } = {}

    for (const result of results) {
      if (!breakdown[result.platform]) {
        breakdown[result.platform] = { reviews: 0, avgSentiment: 0 }
      }

      breakdown[result.platform].reviews += result.reviews.length

      // Calculate average sentiment for this platform
      const sentiments = result.reviews.map((r) => r.sentiment?.score).filter((s) => s !== undefined) as number[]

      if (sentiments.length > 0) {
        const avgSentiment = sentiments.reduce((sum, s) => sum + s, 0) / sentiments.length
        breakdown[result.platform].avgSentiment = Math.round(avgSentiment * 100)
      }
    }

    return breakdown
  }

  private calculateCompanySentiments(results: ScrapedData[]) {
    const sentiments: {
      [company: string]: {
        totalReviews: number
        averageSentiment: number
        platforms: { [platform: string]: number }
      }
    } = {}

    for (const result of results) {
      if (!sentiments[result.company]) {
        sentiments[result.company] = {
          totalReviews: 0,
          averageSentiment: 0,
          platforms: {},
        }
      }

      sentiments[result.company].totalReviews += result.reviews.length
      sentiments[result.company].platforms[result.platform] = result.reviews.length

      // Calculate sentiment
      const companySentiments = result.reviews.map((r) => r.sentiment?.score).filter((s) => s !== undefined) as number[]

      if (companySentiments.length > 0) {
        const avgSentiment = companySentiments.reduce((sum, s) => sum + s, 0) / companySentiments.length
        sentiments[result.company].averageSentiment = Math.round(avgSentiment * 100)
      }
    }

    return sentiments
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }
}
