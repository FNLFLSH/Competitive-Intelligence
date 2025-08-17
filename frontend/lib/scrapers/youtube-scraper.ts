import { BaseScraper, type ScrapedData, type Review } from "./base-scraper"

export class YouTubeScraper extends BaseScraper {
  private apiKey: string

  constructor() {
    super("youtube", "https://www.googleapis.com/youtube/v3")
    this.apiKey = process.env.YOUTUBE_API_KEY || ""
  }

  async scrapeCompany(companyName: string): Promise<ScrapedData> {
    if (!this.apiKey) {
      throw new Error("YouTube API key not configured")
    }

    try {
      const query = `${companyName} review accounting software`
      const searchUrl = `${this.baseUrl}/search?part=snippet&q=${encodeURIComponent(query)}&type=video&maxResults=50&key=${this.apiKey}`

      const response = await this.fetchWithRetry(searchUrl)
      const data = await response.json()

      if (!data.items) {
        return this.createEmptyResult(companyName)
      }

      const reviews: Review[] = []

      for (const video of data.items) {
        // Get video comments
        try {
          const commentsUrl = `${this.baseUrl}/commentThreads?part=snippet&videoId=${video.id.videoId}&maxResults=20&key=${this.apiKey}`
          const commentsResponse = await this.fetchWithRetry(commentsUrl)
          const commentsData = await commentsResponse.json()

          if (commentsData.items) {
            for (const comment of commentsData.items) {
              const commentText = comment.snippet.topLevelComment.snippet.textDisplay

              reviews.push({
                id: this.generateReviewId(companyName, commentText),
                title: video.snippet.title,
                content: this.sanitizeText(commentText),
                author: comment.snippet.topLevelComment.snippet.authorDisplayName,
                date: new Date(comment.snippet.topLevelComment.snippet.publishedAt),
              })
            }
          }
        } catch (error) {
          console.warn(`Failed to get comments for video ${video.id.videoId}:`, error)
        }

        await this.delay(100) // Rate limiting
      }

      return {
        platform: this.platform,
        company: companyName,
        reviews,
        metadata: {
          totalReviews: reviews.length,
          averageRating: 0,
          scrapedAt: new Date(),
        },
      }
    } catch (error) {
      console.error(`YouTube scraping failed for ${companyName}:`, error)
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
