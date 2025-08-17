import { type NextRequest, NextResponse } from "next/server"
import { LinkedInScraper } from "@/lib/scrapers/linkedin-scraper"

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
    const { companies } = body

    if (!companies || !Array.isArray(companies) || companies.length === 0) {
      return NextResponse.json({ error: "Companies array is required" }, { status: 400 })
    }

    const scraper = new LinkedInScraper()
    const results = []
    const errors = []

    for (const company of companies) {
      try {
        console.log(`🔍 Scraping hiring data for ${company}...`)
        const data = await scraper.scrapeCompany(company)
        results.push(data)
        console.log(`✅ ${company}: ${data.reviews.length} posts/updates found`)
      } catch (error) {
        const errorMsg = `Failed to scrape ${company}: ${error}`
        errors.push(errorMsg)
        console.error(`❌ ${errorMsg}`)
      }

      // Rate limiting
      await new Promise((resolve) => setTimeout(resolve, 1000))
    }

    return NextResponse.json({
      success: results.length > 0,
      data: results,
      summary: {
        companiesAnalyzed: results.length,
        totalPosts: results.reduce((sum, r) => sum + r.reviews.length, 0),
        platform: "linkedin",
      },
      errors,
    })
  } catch (error) {
    console.error("Hiring scraping API error:", error)
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 },
    )
  }
}

export async function GET() {
  return NextResponse.json({
    message: "Hiring Intelligence API endpoint",
    platform: "linkedin",
    usage: "POST with { companies: string[] }",
    note: "Scrapes LinkedIn for job postings and hiring trends",
    requiredEnvVar: "LINKEDIN_SESSION_COOKIE",
  })
}
