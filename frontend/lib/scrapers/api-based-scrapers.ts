// Reddit API Scraper (Real Implementation)
export class RealRedditScraper extends BaseScraper {
  private clientId: string
  private clientSecret: string
  private accessToken: string | null = null

  constructor() {
    super("reddit", "https://oauth.reddit.com")
    this.clientId = process.env.REDDIT_CLIENT_ID || ""
    this.clientSecret = process.env.REDDIT_CLIENT_SECRET || ""
  }

  async getAccessToken(): Promise<string> {
    if (this.accessToken) return this.accessToken

    const auth = Buffer.from(`${this.clientId}:${this.clientSecret}`).toString("base64")

    const response = await fetch("https://www.reddit.com/api/v1/access_token", {
      method: "POST",
      headers: {
        Authorization: `Basic ${auth}`,
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "CompetitiveIntelligence/1.0",
      },
      body: "grant_type=client_credentials",
    })

    const data = await response.json()
    this.accessToken = data.access_token
    return this.accessToken
  }

  async scrapeCompany(companyName: string): Promise<ScrapedData> {
    try {
      const accessToken = await this.getAccessToken()

      // Search across relevant subreddits
      const subreddits = ["accounting", "smallbusiness", "entrepreneur", "bookkeeping"]
      const allReviews: Review[] = []

      for (const subreddit of subreddits) {
        const searchUrl = `${this.baseUrl}/r/${subreddit}/search?q=${encodeURIComponent(companyName)}&sort=relevance&limit=25&restrict_sr=1`

        const response = await fetch(searchUrl, {
          headers: {
            Authorization: `Bearer ${accessToken}`,
            "User-Agent": "CompetitiveIntelligence/1.0",
          },
        })

        const data = await response.json()

        if (data.data && data.data.children) {
          const posts = data.data.children
            .filter((item: any) => item.data.selftext || item.data.title)
            .map((item: any) => {
              const content = item.data.selftext || item.data.title
              const sentiment = analyzeVaderSentiment(content)

              return {
                id: item.data.id,
                content: this.sanitizeText(content),
                title: item.data.title,
                author: item.data.author,
                date: new Date(item.data.created_utc * 1000),
                rating: item.data.score,
                sentiment,
                url: `https://reddit.com${item.data.permalink}`,
              }
            })

          allReviews.push(...posts)
        }

        // Rate limiting
        await this.delay(1000)
      }

      return {
        platform: this.platform,
        company: companyName,
        reviews: allReviews,
        metadata: {
          totalReviews: allReviews.length,
          averageRating: allReviews.reduce((sum, r) => sum + (r.rating || 0), 0) / allReviews.length,
          scrapedAt: new Date(),
        },
      }
    } catch (error) {
      console.error(`Reddit scraping failed for ${companyName}:`, error)
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

// Twitter/X API Scraper (Real Implementation)
export class RealTwitterScraper extends BaseScraper {
  private bearerToken: string

  constructor() {
    super("twitter", "https://api.twitter.com/2")
    this.bearerToken = process.env.TWITTER_BEARER_TOKEN || ""
  }

  async scrapeCompany(companyName: string): Promise<ScrapedData> {
    if (!this.bearerToken) {
      throw new Error("Twitter Bearer Token not configured")
    }

    try {
      const query = `${companyName} (accounting OR software OR review) -is:retweet lang:en`
      const url = `${this.baseUrl}/tweets/search/recent?query=${encodeURIComponent(query)}&max_results=100&tweet.fields=created_at,author_id,public_metrics,context_annotations&expansions=author_id&user.fields=username,name`

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${this.bearerToken}`,
        },
      })

      const data = await response.json()

      if (!data.data) {
        return this.createEmptyResult(companyName)
      }

      const users = data.includes?.users || []
      const userMap = new Map(users.map((user: any) => [user.id, user]))

      const reviews: Review[] = data.data.map((tweet: any) => {
        const author = userMap.get(tweet.author_id)
        const sentiment = analyzeVaderSentiment(tweet.text)

        return {
          id: tweet.id,
          content: this.sanitizeText(tweet.text),
          author: author?.username || tweet.author_id,
          date: new Date(tweet.created_at),
          sentiment,
          engagement: {
            likes: tweet.public_metrics?.like_count || 0,
            retweets: tweet.public_metrics?.retweet_count || 0,
            replies: tweet.public_metrics?.reply_count || 0,
          },
          url: `https://twitter.com/${author?.username}/status/${tweet.id}`,
        }
      })

      return {
        platform: this.platform,
        company: companyName,
        reviews,
        metadata: {
          totalReviews: reviews.length,
          averageRating: 0, // Twitter doesn't have ratings
          scrapedAt: new Date(),
        },
      }
    } catch (error) {
      console.error(`Twitter scraping failed for ${companyName}:`, error)
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
