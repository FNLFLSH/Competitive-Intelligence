import { RealG2Scraper, type G2Review } from "./real-g2-scraper"
import { RealGlassdoorScraper, type GlassdoorReview } from "./real-glassdoor-scraper"
import { analyzeSentiment } from "../sentiment/sentiment-analyzer"

export interface ScrapedData {
  platform: string
  company: string
  content: string
  sentiment?: number
  timestamp: Date
  url: string
  rating?: number
  title?: string
  author?: string
  pros?: string[]
  cons?: string[]
  totalReviews?: number
  averageRating?: number
  averageSentiment?: number
}

export interface ScrapingResult {
  success: boolean
  data: ScrapedData[]
  summary: {
    totalReviews: number
    totalCompanies: number
    totalPlatforms: number
    averageSentiment: number
    processingTime: string
    g2Reviews?: number
    glassdoorReviews?: number
    companiesAnalyzed?: number
    avgProcessingTime?: string
  }
  platformBreakdown: Record<string, any>
  companySentiments: Record<string, any>
  errors: string[]
  isLiveData: boolean
}

export class RealScraperManager {
  private g2Scraper: RealG2Scraper
  private glassdoorScraper: RealGlassdoorScraper

  constructor() {
    this.g2Scraper = new RealG2Scraper()
    this.glassdoorScraper = new RealGlassdoorScraper()
  }

  private async delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  async scrapeCompanies(companies: string[]): Promise<ScrapingResult> {
    const startTime = Date.now()
    const allData: ScrapedData[] = []
    const errors: string[] = []
    const platformBreakdown: Record<string, any> = {}
    const companySentiments: Record<string, any> = {}

    console.log(`🚀 Starting live scraping for ${companies.length} companies...`)

    for (const company of companies.slice(0, 5)) {
      // Limit to 5 companies for demo
      console.log(`\n📊 Processing company: ${company}`)

      try {
        // Scrape G2
        console.log(`🔍 Scraping G2 for ${company}...`)
        const g2Reviews = await this.g2Scraper.scrapeCompany(company)
        await this.delay(3000) // Rate limiting

        // Process G2 data
        const g2Data = await this.processReviews(g2Reviews, "g2", company)
        allData.push(...g2Data)

        // Scrape Glassdoor
        console.log(`🔍 Scraping Glassdoor for ${company}...`)
        const glassdoorReviews = await this.glassdoorScraper.scrapeCompany(company)
        await this.delay(3000) // Rate limiting

        // Process Glassdoor data
        const glassdoorData = await this.processReviews(glassdoorReviews, "glassdoor", company)
        allData.push(...glassdoorData)

        // Calculate company sentiment
        const companyData = [...g2Data, ...glassdoorData]
        if (companyData.length > 0) {
          const avgSentiment = companyData.reduce((sum, item) => sum + (item.sentiment || 0), 0) / companyData.length
          const avgRating = companyData.reduce((sum, item) => sum + (item.rating || 0), 0) / companyData.length

          companySentiments[company] = {
            averageSentiment: Math.round(avgSentiment * 1000) / 1000,
            totalReviews: companyData.length,
            averageRating: Math.round(avgRating * 10) / 10,
            platforms: {
              g2: g2Data.length,
              glassdoor: glassdoorData.length,
            },
          }
        }
      } catch (error) {
        const errorMsg = `Failed to scrape ${company}: ${error}`
        console.error(`❌ ${errorMsg}`)
        errors.push(errorMsg)
      }
    }

    // Calculate platform breakdown
    platformBreakdown.g2 = {
      count: allData.filter((d) => d.platform === "g2").length,
      avgSentiment: this.calculateAverageSentiment(allData.filter((d) => d.platform === "g2")),
    }

    platformBreakdown.glassdoor = {
      count: allData.filter((d) => d.platform === "glassdoor").length,
      avgSentiment: this.calculateAverageSentiment(allData.filter((d) => d.platform === "glassdoor")),
    }

    const processingTime = ((Date.now() - startTime) / 1000).toFixed(2)
    const averageSentiment = this.calculateAverageSentiment(allData)

    const result: ScrapingResult = {
      success: allData.length > 0,
      data: allData,
      summary: {
        totalReviews: allData.length,
        totalCompanies: Object.keys(companySentiments).length,
        totalPlatforms: 2,
        averageSentiment: averageSentiment,
        processingTime: processingTime,
        g2Reviews: platformBreakdown.g2?.count || 0,
        glassdoorReviews: platformBreakdown.glassdoor?.count || 0,
        companiesAnalyzed: Object.keys(companySentiments).length,
        avgProcessingTime: `${processingTime}s`,
      },
      platformBreakdown,
      companySentiments,
      errors,
      isLiveData: true,
    }

    console.log(`\n✅ Live scraping completed!`)
    console.log(`📊 Total reviews: ${allData.length}`)
    console.log(`⏱️ Processing time: ${processingTime}s`)
    console.log(`🎯 Companies analyzed: ${Object.keys(companySentiments).length}`)

    return result
  }

  private async processReviews(
    reviews: (G2Review | GlassdoorReview)[],
    platform: string,
    company: string,
  ): Promise<ScrapedData[]> {
    const processedData: ScrapedData[] = []

    for (const review of reviews) {
      try {
        const sentiment = await analyzeSentiment(review.content)

        processedData.push({
          platform,
          company: company.toLowerCase(),
          content: review.content,
          sentiment: sentiment.compound,
          timestamp: new Date(review.date),
          url: review.url,
          rating: review.rating,
          title: review.title,
          author: review.author,
          pros: review.pros,
          cons: review.cons,
        })
      } catch (error) {
        console.error(`Error processing review for ${company}:`, error)
      }
    }

    return processedData
  }

  private calculateAverageSentiment(data: ScrapedData[]): number {
    if (data.length === 0) return 0
    const sum = data.reduce((acc, item) => acc + (item.sentiment || 0), 0)
    return Math.round((sum / data.length) * 1000) / 1000
  }
}
