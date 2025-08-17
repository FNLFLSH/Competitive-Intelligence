import { type NextRequest, NextResponse } from "next/server"
import { ScraperManager } from "@/lib/scrapers/scraper-manager"

const companyData = [
  "Sage",
  "QuickBooks",
  "Xero",
  "NetSuite",
  "FreshBooks",
  "Wave Accounting",
  "Zoho Books",
  "KashFlow",
  "FreeAgent",
  "Clear Books",
  "Receipt Bank",
  "Dext",
  "AutoEntry",
  "Hubdoc",
  "Expensify",
  "Concur",
  "Rydoo",
  "Certify",
  "Chrome River",
  "Abacus",
  "Divvy",
  "Brex",
  "Ramp",
  "Airbase",
  "Tipalti",
  "Bill.com",
  "MineralTree",
  "AvidXchange",
  "Stampli",
  "AppZen",
  "Coupa",
  "Ariba",
  "Jaggaer",
  "Ivalua",
  "Procurify",
]

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { companies, platforms, includeSentiment = true } = body

    if (!companies || !Array.isArray(companies) || companies.length === 0) {
      return NextResponse.json({ error: "Companies array is required" }, { status: 400 })
    }

    const manager = new ScraperManager()

    // Filter out LinkedIn for sentiment analysis (hiring only)
    const sentimentPlatforms = (platforms || ["twitter", "reddit", "g2", "youtube", "glassdoor"]).filter(
      (p) => p !== "linkedin",
    )

    const results = await manager.scrapeCompanies(companies, sentimentPlatforms, { includeSentiment })

    return NextResponse.json(results)
  } catch (error) {
    console.error("Scraping API error:", error)
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 },
    )
  }
}

export async function GET() {
  return NextResponse.json({
    message: "Competitive Intelligence Scraping API",
    endpoints: {
      "POST /api/scrape": "Scrape companies for sentiment analysis",
      "POST /api/scrape/hiring": "Scrape LinkedIn for hiring intelligence",
      "POST /api/scrape/test": "Test scraping with sample companies",
    },
    supportedPlatforms: ["twitter", "reddit", "g2", "youtube", "glassdoor"],
  })
}
