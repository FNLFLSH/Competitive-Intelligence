export interface ScrapedPost {
  id: string
  content: string
  author: string
  timestamp: Date
  platform: string
  url: string
  engagement?: {
    likes: number
    shares: number
    comments: number
  }
  sentiment?: number
}

export interface ScrapedComment {
  id: string
  content: string
  author: string
  timestamp: Date
  parentId?: string
  replies?: ScrapedComment[]
  sentiment?: number
}

export interface ScrapedData {
  platform: string
  company: string
  content: string
  sentiment?: number
  timestamp: Date | string
  url: string
  rating?: number
  title?: string
  author?: string
  pros?: string[]
  cons?: string[]
  reviewerRole?: string
  companySize?: string
  productName?: string
  employmentStatus?: string
  recommendation?: boolean
  outlook?: string
  location?: string
}

export interface ScrapingResult {
  success: boolean
  data: ScrapedData[]
  error?: string
  company: string
  platform: string
  totalReviews: number
  averageRating?: number
  averageSentiment?: number
}

export abstract class BaseScraper {
  protected platform: string
  protected rateLimitDelay = 1000

  constructor(platform: string) {
    this.platform = platform
  }

  abstract scrape(query: string): Promise<any[]>

  protected delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  protected parseDate(dateString: string): Date {
    return new Date(dateString)
  }

  async scrapeCompany(company: string): Promise<ScrapedData> {
    const posts = await this.scrape(company)

    return {
      platform: this.platform,
      company,
      reviews: posts,
      timestamp: new Date(),
      totalReviews: posts.length,
    }
  }
}
