import puppeteer from "puppeteer"
import { insertSentimentData, type SentimentData } from "@/lib/database/supabase-client"
import { analyzeSentiment } from "@/lib/sentiment/vader-sentiment"

export interface ScrapingResult {
  success: boolean
  totalReviews: number
  companiesProcessed: number
  platformBreakdown: {
    g2: number
    glassdoor: number
  }
  averageSentiment: number
  storedInSupabase: boolean
  storedCount: number
  processingTime: string
  errors: string[]
  companyResults: CompanyResult[]
  message: string
  timestamp: string
  requestId: string
}

export interface CompanyResult {
  company: string
  totalReviews: number
  averageSentiment: number
  averageRating: number
  platforms: {
    g2: { reviews: number; avgSentiment: number; avgRating: number }
    glassdoor: { reviews: number; avgSentiment: number; avgRating: number }
  }
}

export class EnhancedRealScraperManager {
  private browser: any = null
  private requestId: string

  constructor() {
    this.requestId = Math.random().toString(36).substring(2, 15)
  }

  async initialize() {
    if (!this.browser) {
      this.browser = await puppeteer.launch({
        headless: true,
        args: [
          "--no-sandbox",
          "--disable-setuid-sandbox",
          "--disable-dev-shm-usage",
          "--disable-accelerated-2d-canvas",
          "--no-first-run",
          "--no-zygote",
          "--disable-gpu",
        ],
      })
    }
  }

  async scrapeAndAnalyze(companies: string[]): Promise<ScrapingResult> {
    const startTime = Date.now()
    const errors: string[] = []
    const allSentimentData: SentimentData[] = []
    const companyResults: CompanyResult[] = []

    console.log(`🚀 Starting enhanced scraping for companies: ${companies.join(", ")}`)

    for (const company of companies) {
      try {
        console.log(`📊 Processing company: ${company}`)

        // Scrape G2
        const g2Data = await this.scrapeG2(company)

        // Wait between platforms
        await this.delay(5000)

        // Scrape Glassdoor
        const glassdoorData = await this.scrapeGlassdoor(company)

        // Combine all reviews for this company
        const companyReviews = [...g2Data, ...glassdoorData]

        // Analyze sentiment for each review
        const analyzedReviews = companyReviews.map((review) => ({
          ...review,
          ...analyzeSentiment(review.content),
        }))

        allSentimentData.push(...analyzedReviews)

        // Calculate company-level metrics
        const totalReviews = analyzedReviews.length
        const avgSentiment =
          totalReviews > 0 ? analyzedReviews.reduce((sum, r) => sum + (r.sentiment_score || 0), 0) / totalReviews : 0
        const avgRating =
          totalReviews > 0
            ? analyzedReviews.filter((r) => r.rating).reduce((sum, r) => sum + (r.rating || 0), 0) /
              analyzedReviews.filter((r) => r.rating).length
            : 0

        // Platform-specific metrics
        const g2Reviews = analyzedReviews.filter((r) => r.platform === "g2")
        const glassdoorReviews = analyzedReviews.filter((r) => r.platform === "glassdoor")

        companyResults.push({
          company,
          totalReviews,
          averageSentiment: avgSentiment,
          averageRating: avgRating || 0,
          platforms: {
            g2: {
              reviews: g2Reviews.length,
              avgSentiment:
                g2Reviews.length > 0
                  ? g2Reviews.reduce((sum, r) => sum + (r.sentiment_score || 0), 0) / g2Reviews.length
                  : 0,
              avgRating:
                g2Reviews.filter((r) => r.rating).length > 0
                  ? g2Reviews.filter((r) => r.rating).reduce((sum, r) => sum + (r.rating || 0), 0) /
                    g2Reviews.filter((r) => r.rating).length
                  : 0,
            },
            glassdoor: {
              reviews: glassdoorReviews.length,
              avgSentiment:
                glassdoorReviews.length > 0
                  ? glassdoorReviews.reduce((sum, r) => sum + (r.sentiment_score || 0), 0) / glassdoorReviews.length
                  : 0,
              avgRating:
                glassdoorReviews.filter((r) => r.rating).length > 0
                  ? glassdoorReviews.filter((r) => r.rating).reduce((sum, r) => sum + (r.rating || 0), 0) /
                    glassdoorReviews.filter((r) => r.rating).length
                  : 0,
            },
          },
        })

        // Add delay between companies to avoid rate limiting
        if (companies.indexOf(company) < companies.length - 1) {
          await new Promise((resolve) => setTimeout(resolve, 3000))
        }
      } catch (error) {
        const errorMsg = `Failed to process ${company}: ${error instanceof Error ? error.message : "Unknown error"}`
        errors.push(errorMsg)
        console.error(`❌ ${errorMsg}`)
      }
    }

    // Store in Supabase
    let storedInSupabase = false
    let storedCount = 0

    if (allSentimentData.length > 0) {
      try {
        const result = await insertSentimentData(allSentimentData)
        storedInSupabase = true
        storedCount = result?.length || 0
        console.log(`✅ Stored ${storedCount} records in Supabase`)
      } catch (error) {
        const errorMsg = `Failed to store data in Supabase: ${error instanceof Error ? error.message : "Unknown error"}`
        errors.push(errorMsg)
        console.error(`❌ ${errorMsg}`)
      }
    }

    const processingTime = `${((Date.now() - startTime) / 1000).toFixed(1)}s`
    const totalReviews = allSentimentData.length
    const averageSentiment =
      totalReviews > 0 ? allSentimentData.reduce((sum, r) => sum + (r.sentiment_score || 0), 0) / totalReviews : 0

    const result: ScrapingResult = {
      success: errors.length === 0 && totalReviews > 0,
      totalReviews,
      companiesProcessed: companyResults.length,
      platformBreakdown: {
        g2: allSentimentData.filter((r) => r.platform === "g2").length,
        glassdoor: allSentimentData.filter((r) => r.platform === "glassdoor").length,
      },
      averageSentiment,
      storedInSupabase,
      storedCount,
      processingTime,
      errors,
      companyResults,
      message: `Processed ${companyResults.length} companies with ${totalReviews} total reviews`,
      timestamp: new Date().toISOString(),
      requestId: this.requestId,
    }

    console.log(`🏁 Scraping completed:`, result)
    return result
  }

  private async scrapeG2(company: string): Promise<SentimentData[]> {
    const page = await this.browser.newPage()
    const results: SentimentData[] = []

    try {
      // Set user agent
      await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
      )

      // Search for company on G2
      const searchUrl = `https://www.g2.com/search?query=${encodeURIComponent(company)}`
      await page.goto(searchUrl, { waitUntil: "networkidle2", timeout: 30000 })

      // Find and click on the first product result
      const productLink = await page.$('a[href*="/products/"]')
      if (!productLink) {
        console.log(`No G2 product found for ${company}`)
        return results
      }

      await productLink.click()
      await page.waitForLoadState("networkidle")

      // Navigate to reviews
      const reviewsUrl = page.url() + "/reviews"
      await page.goto(reviewsUrl, { waitUntil: "networkidle2" })

      // Scrape reviews
      const reviews = await page.$$eval('[data-testid="review-card"]', (elements) => {
        return elements.slice(0, 10).map((el) => {
          const titleEl = el.querySelector('[data-testid="review-title"]')
          const contentEl = el.querySelector('[data-testid="review-body"]')
          const authorEl = el.querySelector('[data-testid="reviewer-name"]')
          const ratingEl = el.querySelector('[data-testid="star-rating"]')
          const prosEl = el.querySelector('[data-testid="pros"]')
          const consEl = el.querySelector('[data-testid="cons"]')

          return {
            title: titleEl?.textContent?.trim() || "",
            content: contentEl?.textContent?.trim() || "",
            author: authorEl?.textContent?.trim() || "",
            rating: ratingEl ? Number.parseInt(ratingEl.getAttribute("aria-label")?.match(/\d+/)?.[0] || "0") : 0,
            pros: prosEl?.textContent?.trim() || "",
            cons: consEl?.textContent?.trim() || "",
          }
        })
      })

      // Process reviews with sentiment analysis
      for (const review of reviews) {
        if (review.content) {
          const sentiment = analyzeSentiment(review.content)

          results.push({
            company,
            platform: "g2",
            title: review.title,
            content: review.content,
            author: review.author,
            url: page.url(),
            sentiment_score: sentiment.compound,
            sentiment_label:
              sentiment.compound > 0.05 ? "positive" : sentiment.compound < -0.05 ? "negative" : "neutral",
            sentiment_confidence: Math.abs(sentiment.compound),
            rating: review.rating,
            pros: review.pros ? [review.pros] : undefined,
            cons: review.cons ? [review.cons] : undefined,
            scraped_at: new Date().toISOString(),
          })
        }
      }

      console.log(`✅ Scraped ${results.length} G2 reviews for ${company}`)
    } catch (error) {
      console.error(`Error scraping G2 for ${company}:`, error)
    } finally {
      await page.close()
    }

    return results
  }

  private async scrapeGlassdoor(company: string): Promise<SentimentData[]> {
    const page = await this.browser.newPage()
    const results: SentimentData[] = []

    try {
      await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
      )

      // Search for company on Glassdoor
      const searchUrl = `https://www.glassdoor.com/Search/results.htm?keyword=${encodeURIComponent(company)}`
      await page.goto(searchUrl, { waitUntil: "networkidle2", timeout: 30000 })

      // Find and click on company result
      const companyLink = await page.$('a[data-test="employer-name"]')
      if (!companyLink) {
        console.log(`No Glassdoor company found for ${company}`)
        return results
      }

      await companyLink.click()
      await page.waitForLoadState("networkidle")

      // Navigate to reviews
      const reviewsLink = await page.$('a[data-test="ReviewsTab"]')
      if (reviewsLink) {
        await reviewsLink.click()
        await page.waitForLoadState("networkidle")
      }

      // Scrape reviews
      const reviews = await page.$$eval('[data-test="employerReview"]', (elements) => {
        return elements.slice(0, 10).map((el) => {
          const titleEl = el.querySelector('[data-test="review-title"]')
          const contentEl = el.querySelector('[data-test="review-text"]')
          const authorEl = el.querySelector('[data-test="reviewer-info"]')
          const ratingEl = el.querySelector('[data-test="rating"]')
          const prosEl = el.querySelector('[data-test="pros"]')
          const consEl = el.querySelector('[data-test="cons"]')

          return {
            title: titleEl?.textContent?.trim() || "",
            content: contentEl?.textContent?.trim() || "",
            author: authorEl?.textContent?.trim() || "",
            rating: ratingEl ? Number.parseFloat(ratingEl.textContent || "0") : 0,
            pros: prosEl?.textContent?.trim() || "",
            cons: consEl?.textContent?.trim() || "",
          }
        })
      })

      // Process reviews with sentiment analysis
      for (const review of reviews) {
        if (review.content) {
          const sentiment = analyzeSentiment(review.content)

          results.push({
            company,
            platform: "glassdoor",
            title: review.title,
            content: review.content,
            author: review.author,
            url: page.url(),
            sentiment_score: sentiment.compound,
            sentiment_label:
              sentiment.compound > 0.05 ? "positive" : sentiment.compound < -0.05 ? "negative" : "neutral",
            sentiment_confidence: Math.abs(sentiment.compound),
            rating: review.rating,
            pros: review.pros ? [review.pros] : undefined,
            cons: review.cons ? [review.cons] : undefined,
            employment_status: "current", // Default assumption
            scraped_at: new Date().toISOString(),
          })
        }
      }

      console.log(`✅ Scraped ${results.length} Glassdoor reviews for ${company}`)
    } catch (error) {
      console.error(`Error scraping Glassdoor for ${company}:`, error)
    } finally {
      await page.close()
    }

    return results
  }

  private async delay(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  private async cleanup() {
    if (this.browser) {
      await this.browser.close()
      this.browser = null
    }
  }

  async getStoredAnalysis(company?: string) {
    try {
      // This would query your Supabase database
      // For now, return a placeholder response
      return {
        data: [],
        error: null,
      }
    } catch (error) {
      return {
        data: null,
        error: error instanceof Error ? error.message : "Unknown error",
      }
    }
  }
}
