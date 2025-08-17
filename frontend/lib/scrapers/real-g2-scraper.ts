import puppeteer from "puppeteer"

export interface G2Review {
  title: string
  content: string
  rating: number
  author: string
  date: string
  pros: string[]
  cons: string[]
  url: string
}

export class RealG2Scraper {
  private async delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  async scrapeCompany(companyName: string): Promise<G2Review[]> {
    let browser
    const reviews: G2Review[] = []

    try {
      console.log(`🔍 Starting G2 scraping for: ${companyName}`)

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

      // Search for the company on G2
      const searchUrl = `https://www.g2.com/search?query=${encodeURIComponent(companyName)}`
      console.log(`📍 Navigating to: ${searchUrl}`)

      await page.goto(searchUrl, { waitUntil: "networkidle2", timeout: 30000 })
      await this.delay(2000)

      // Find the first product link
      const productLinks = await page.$$eval('a[href*="/products/"]', (links) =>
        links.map((link) => (link as HTMLAnchorElement).href).filter((href) => href.includes("/products/")),
      )

      if (productLinks.length === 0) {
        console.log(`❌ No G2 product page found for ${companyName}`)
        return []
      }

      const productUrl = productLinks[0]
      console.log(`📍 Found product page: ${productUrl}`)

      // Navigate to reviews page
      const reviewsUrl = productUrl.replace(/\/$/, "") + "/reviews"
      await page.goto(reviewsUrl, { waitUntil: "networkidle2", timeout: 30000 })
      await this.delay(3000)

      // Scroll to load more reviews
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight)
      })
      await this.delay(2000)

      // Extract reviews with multiple selector strategies
      const extractedReviews = await page.evaluate(() => {
        const reviewElements = document.querySelectorAll(
          '[data-testid="review-card"], .review-card, .paper.paper--white.paper--box, [class*="review"]',
        )
        const reviews: any[] = []

        reviewElements.forEach((element, index) => {
          if (index >= 10) return // Limit to 10 reviews

          try {
            // Multiple strategies for title
            const titleSelectors = ['[data-testid="review-title"]', ".review-title", "h3", '[class*="title"]']

            let title = ""
            for (const selector of titleSelectors) {
              const titleEl = element.querySelector(selector)
              if (titleEl?.textContent?.trim()) {
                title = titleEl.textContent.trim()
                break
              }
            }

            // Multiple strategies for content
            const contentSelectors = [
              '[data-testid="review-body"]',
              ".review-body",
              ".review-content",
              "p",
              '[class*="content"]',
            ]

            let content = ""
            for (const selector of contentSelectors) {
              const contentEl = element.querySelector(selector)
              if (contentEl?.textContent?.trim() && contentEl.textContent.length > 50) {
                content = contentEl.textContent.trim()
                break
              }
            }

            // Extract rating
            const ratingEl = element.querySelector('[class*="star"], [data-testid*="rating"]')
            let rating = 0
            if (ratingEl) {
              const ratingText = ratingEl.textContent || ratingEl.getAttribute("aria-label") || ""
              const ratingMatch = ratingText.match(/(\d+(?:\.\d+)?)/)
              rating = ratingMatch ? Number.parseFloat(ratingMatch[1]) : 0
            }

            // Extract author
            const authorSelectors = [
              '[data-testid="reviewer-name"]',
              ".reviewer-name",
              '[class*="author"]',
              '[class*="user"]',
            ]

            let author = "Anonymous"
            for (const selector of authorSelectors) {
              const authorEl = element.querySelector(selector)
              if (authorEl?.textContent?.trim()) {
                author = authorEl.textContent.trim()
                break
              }
            }

            // Extract pros and cons
            const prosEl = element.querySelector('[data-testid="pros"], .pros, [class*="pros"]')
            const consEl = element.querySelector('[data-testid="cons"], .cons, [class*="cons"]')

            const pros = prosEl?.textContent?.trim() ? [prosEl.textContent.trim()] : []
            const cons = consEl?.textContent?.trim() ? [consEl.textContent.trim()] : []

            if (title || content) {
              reviews.push({
                title: title || "Review",
                content: content || title || "No content available",
                rating: rating,
                author: author,
                date: new Date().toISOString(),
                pros: pros,
                cons: cons,
                url: window.location.href,
              })
            }
          } catch (error) {
            console.error("Error extracting review:", error)
          }
        })

        return reviews
      })

      reviews.push(...extractedReviews)
      console.log(`✅ G2 scraping completed for ${companyName}: ${reviews.length} reviews`)
    } catch (error) {
      console.error(`❌ G2 scraping error for ${companyName}:`, error)
    } finally {
      if (browser) {
        await browser.close()
      }
    }

    return reviews
  }
}
