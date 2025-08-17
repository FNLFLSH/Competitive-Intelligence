import puppeteer from "puppeteer"

export interface GlassdoorReview {
  title: string
  content: string
  rating: number
  author: string
  date: string
  pros: string[]
  cons: string[]
  url: string
  jobTitle?: string
  recommendation?: string
}

export class RealGlassdoorScraper {
  private async delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  async scrapeCompany(companyName: string): Promise<GlassdoorReview[]> {
    let browser
    const reviews: GlassdoorReview[] = []

    try {
      console.log(`🔍 Starting Glassdoor scraping for: ${companyName}`)

      browser = await puppeteer.launch({
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

      const page = await browser.newPage()

      // Set realistic user agent
      await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
      )

      // Search for the company on Glassdoor
      const searchUrl = `https://www.glassdoor.com/Search/results.htm?keyword=${encodeURIComponent(companyName)}`
      console.log(`📍 Navigating to: ${searchUrl}`)

      await page.goto(searchUrl, { waitUntil: "networkidle2", timeout: 30000 })
      await this.delay(3000)

      // Handle potential popups
      try {
        const closeButton = await page.$('[data-test="close-x"]')
        if (closeButton) {
          await closeButton.click()
          await this.delay(1000)
        }
      } catch (e) {
        // Ignore popup errors
      }

      // Find company link
      const companyLinks = await page.$$eval('a[href*="/Overview/"]', (links) =>
        links.map((link) => (link as HTMLAnchorElement).href),
      )

      if (companyLinks.length === 0) {
        console.log(`❌ No Glassdoor company page found for ${companyName}`)
        return []
      }

      const companyUrl = companyLinks[0]
      const reviewsUrl = companyUrl.replace("/Overview/", "/Reviews/")
      console.log(`📍 Found reviews page: ${reviewsUrl}`)

      await page.goto(reviewsUrl, { waitUntil: "networkidle2", timeout: 30000 })
      await this.delay(3000)

      // Scroll to load more reviews
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight)
      })
      await this.delay(2000)

      // Extract reviews
      const extractedReviews = await page.evaluate(() => {
        const reviewElements = document.querySelectorAll(
          '[data-test="review"], .review, .employeeReview, [class*="review"]',
        )
        const reviews: any[] = []

        reviewElements.forEach((element, index) => {
          if (index >= 10) return // Limit to 10 reviews

          try {
            // Extract title
            const titleSelectors = ['[data-test="review-title"]', ".reviewTitle", ".summary", "h2", '[class*="title"]']

            let title = ""
            for (const selector of titleSelectors) {
              const titleEl = element.querySelector(selector)
              if (titleEl?.textContent?.trim()) {
                title = titleEl.textContent.trim()
                break
              }
            }

            // Extract content/description
            const contentSelectors = [
              '[data-test="review-text"]',
              ".reviewText",
              ".description",
              ".cont",
              '[class*="description"]',
            ]

            let content = ""
            for (const selector of contentSelectors) {
              const contentEl = element.querySelector(selector)
              if (contentEl?.textContent?.trim() && contentEl.textContent.length > 30) {
                content = contentEl.textContent.trim()
                break
              }
            }

            // Extract rating
            const ratingSelectors = ['[data-test="rating"]', ".rating", ".ratingNumber", '[class*="rating"]']

            let rating = 0
            for (const selector of ratingSelectors) {
              const ratingEl = element.querySelector(selector)
              if (ratingEl) {
                const ratingText = ratingEl.textContent || ratingEl.getAttribute("aria-label") || ""
                const ratingMatch = ratingText.match(/(\d+(?:\.\d+)?)/)
                if (ratingMatch) {
                  rating = Number.parseFloat(ratingMatch[1])
                  break
                }
              }
            }

            // Extract job title and author info
            const authorSelectors = ['[data-test="author-title"]', ".authorTitle", ".jobTitle", '[class*="job"]']

            let jobTitle = ""
            for (const selector of authorSelectors) {
              const authorEl = element.querySelector(selector)
              if (authorEl?.textContent?.trim()) {
                jobTitle = authorEl.textContent.trim()
                break
              }
            }

            // Extract pros
            const prosSelectors = ['[data-test="pros"]', ".pros", ".v2__EIReviewDetailsV2__prosText", '[class*="pros"]']

            let pros: string[] = []
            for (const selector of prosSelectors) {
              const prosEl = element.querySelector(selector)
              if (prosEl?.textContent?.trim()) {
                pros = [prosEl.textContent.trim()]
                break
              }
            }

            // Extract cons
            const consSelectors = ['[data-test="cons"]', ".cons", ".v2__EIReviewDetailsV2__consText", '[class*="cons"]']

            let cons: string[] = []
            for (const selector of consSelectors) {
              const consEl = element.querySelector(selector)
              if (consEl?.textContent?.trim()) {
                cons = [consEl.textContent.trim()]
                break
              }
            }

            if (title || content) {
              reviews.push({
                title: title || "Employee Review",
                content: content || title || "No content available",
                rating: rating,
                author: "Anonymous Employee",
                date: new Date().toISOString(),
                pros: pros,
                cons: cons,
                url: window.location.href,
                jobTitle: jobTitle || "Employee",
                recommendation: rating >= 4 ? "Recommends" : rating <= 2 ? "Does not recommend" : "Neutral",
              })
            }
          } catch (error) {
            console.error("Error extracting Glassdoor review:", error)
          }
        })

        return reviews
      })

      reviews.push(...extractedReviews)
      console.log(`✅ Glassdoor scraping completed for ${companyName}: ${reviews.length} reviews`)
    } catch (error) {
      console.error(`❌ Glassdoor scraping error for ${companyName}:`, error)
    } finally {
      if (browser) {
        await browser.close()
      }
    }

    return reviews
  }
}
