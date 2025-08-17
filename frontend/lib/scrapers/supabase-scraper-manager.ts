import { RealScraperManager, type ScrapingResult } from "./real-scraper-manager"
import { insertSentimentData, getSentimentData, getCompanySentimentSummary, type SentimentData } from "../database/supabase-client"

export class SupabaseScraperManager extends RealScraperManager {
  async scrapeAndStore(
    companies: string[],
    platforms?: string[],
  ): Promise<ScrapingResult & { stored: boolean; storedCount?: number }> {
    console.log("🚀 Starting scraping with Supabase storage...")

    // First, scrape the data using the parent class
    const scrapingResult = await super.scrapeCompanies(companies)

    if (!scrapingResult.success || scrapingResult.data.length === 0) {
      return { ...scrapingResult, stored: false }
    }

    try {
      // Transform scraped data to Supabase format
      const supabaseData: SentimentData[] = scrapingResult.data.map((item) => ({
        company: item.company,
        platform: item.platform,
        title: item.title,
        content: item.content,
        author: item.author,
        url: item.url,
        sentiment_score: item.sentiment,
        sentiment_label: this.getSentimentLabel(item.sentiment || 0),
        rating: item.rating,
        pros: item.pros,
        cons: item.cons,
        review_date: item.timestamp.toISOString(),
        scraped_at: new Date().toISOString(),
        raw_data: {
          originalData: item,
          scrapingMetadata: {
            scrapedAt: new Date().toISOString(),
            version: "1.0",
          },
        },
      }))

      // Store in Supabase
      console.log(`💾 Storing ${supabaseData.length} records in Supabase...`)
      const storeResult = await insertSentimentData(supabaseData)

      if (storeResult.success) {
        console.log(`✅ Successfully stored ${storeResult.count} records in Supabase`)
        return {
          ...scrapingResult,
          stored: true,
          storedCount: storeResult.count,
        }
      } else {
        console.error("❌ Failed to store data in Supabase:", storeResult.error)
        return {
          ...scrapingResult,
          stored: false,
          errors: [...scrapingResult.errors, `Supabase storage failed: ${storeResult.error}`],
        }
      }
    } catch (error) {
      console.error("❌ Error during Supabase storage:", error)
      return {
        ...scrapingResult,
        stored: false,
        errors: [
          ...scrapingResult.errors,
          `Storage error: ${error instanceof Error ? error.message : "Unknown error"}`,
        ],
      }
    }
  }

  private getSentimentLabel(score: number): "positive" | "negative" | "neutral" {
    if (score > 0.1) return "positive"
    if (score < -0.1) return "negative"
    return "neutral"
  }

  async getStoredData(filters?: {
    company?: string
    platform?: string
    limit?: number
    offset?: number
  }) {
    return await getSentimentData(filters?.company, filters?.platform, filters?.limit)
  }

  async getCompanyAnalysis(company: string) {
    return await getCompanySentimentSummary(company)
  }
}
