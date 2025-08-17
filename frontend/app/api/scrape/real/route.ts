import { type NextRequest, NextResponse } from "next/server"
import { RealScraperManager } from "@/lib/scrapers/real-scraper-manager"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { companies, platforms, includeSentiment = true } = body

    if (!companies || !Array.isArray(companies) || companies.length === 0) {
      return NextResponse.json({ error: "Companies array is required" }, { status: 400 })
    }

    // Validate environment variables
    const missingEnvVars = []
    if (!process.env.REDDIT_CLIENT_ID) missingEnvVars.push("REDDIT_CLIENT_ID")
    if (!process.env.REDDIT_CLIENT_SECRET) missingEnvVars.push("REDDIT_CLIENT_SECRET")
    if (!process.env.TWITTER_BEARER_TOKEN) missingEnvVars.push("TWITTER_BEARER_TOKEN")

    if (missingEnvVars.length > 0) {
      return NextResponse.json(
        {
          error: "Missing required environment variables",
          missing: missingEnvVars,
          note: "Some scrapers may not work without proper API credentials",
        },
        { status: 400 },
      )
    }

    const manager = new RealScraperManager()
    const results = await manager.scrapeCompanies(companies, platforms, { includeSentiment })

    return NextResponse.json({
      ...results,
      note: "This is REAL scraped data from live sources",
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error("Real scraping API error:", error)
    return NextResponse.json(
      {
        error: "Internal server error",
        details: error instanceof Error ? error.message : "Unknown error",
        type: "real_scraping_error",
      },
      { status: 500 },
    )
  }
}

export async function GET() {
  return NextResponse.json({
    message: "Real Competitive Intelligence Scraping API",
    type: "REAL_DATA_COLLECTION",
    supportedPlatforms: ["g2", "glassdoor", "reddit", "twitter"],
    requirements: {
      envVars: ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "TWITTER_BEARER_TOKEN"],
      dependencies: ["puppeteer"],
    },
    warning: "This endpoint performs real web scraping. Use responsibly and respect rate limits.",
  })
}
