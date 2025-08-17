import { type NextRequest, NextResponse } from "next/server"
import { SupabaseScraperManager } from "@/lib/scrapers/supabase-scraper-manager"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { companies, platforms, action = "scrape" } = body

    if (!companies || !Array.isArray(companies) || companies.length === 0) {
      return NextResponse.json({ error: "Companies array is required" }, { status: 400 })
    }

    const manager = new SupabaseScraperManager()

    if (action === "scrape") {
      // Scrape and store new data
      const result = await manager.scrapeAndStore(companies, platforms)

      return NextResponse.json({
        ...result,
        message: result.stored
          ? `Successfully scraped and stored ${result.storedCount} records`
          : "Scraping completed but storage failed",
        timestamp: new Date().toISOString(),
      })
    } else if (action === "retrieve") {
      // Retrieve stored data
      const { data, error } = await manager.getStoredData({
        company: companies[0], // Use first company for filtering
        limit: 100,
      })

      if (error) {
        return NextResponse.json({ error }, { status: 500 })
      }

      return NextResponse.json({
        success: true,
        data,
        count: data.length,
        message: `Retrieved ${data.length} stored records`,
      })
    } else {
      return NextResponse.json({ error: 'Invalid action. Use "scrape" or "retrieve"' }, { status: 400 })
    }
  } catch (error) {
    console.error("Supabase scraping API error:", error)
    return NextResponse.json(
      {
        error: "Internal server error",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const company = searchParams.get("company")
  const action = searchParams.get("action") || "summary"

  try {
    const manager = new SupabaseScraperManager()

    if (action === "summary" && company) {
      const { data, error } = await manager.getCompanyAnalysis(company)

      if (error) {
        return NextResponse.json({ error }, { status: 500 })
      }

      return NextResponse.json({
        success: true,
        company,
        summary: data,
        timestamp: new Date().toISOString(),
      })
    } else if (action === "list") {
      const { data, error } = await manager.getStoredData({
        company: company || undefined,
        limit: 50,
      })

      if (error) {
        return NextResponse.json({ error }, { status: 500 })
      }

      return NextResponse.json({
        success: true,
        data,
        count: data.length,
      })
    } else {
      return NextResponse.json({
        message: "Supabase Sentiment Data API",
        endpoints: {
          "POST /": "Scrape and store data",
          "GET /?company=name&action=summary": "Get company summary",
          "GET /?action=list": "List stored data",
        },
      })
    }
  } catch (error) {
    console.error("Supabase API GET error:", error)
    return NextResponse.json(
      {
        error: "Internal server error",
        details: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}
