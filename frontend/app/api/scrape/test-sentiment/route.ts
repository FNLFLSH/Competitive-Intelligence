import { type NextRequest, NextResponse } from "next/server"
import { insertSentimentData, getSentimentData, type SentimentData } from "@/lib/database/supabase-client"

export async function POST(request: NextRequest) {
  try {
    // Test data to insert
    const testData: SentimentData[] = [
      {
        company: "Test Company",
        platform: "g2",
        content: "This is a great product with excellent features!",
        sentiment_score: 0.8,
        sentiment_label: "positive",
        sentiment_confidence: 0.9,
        rating: 5,
        author: "Test User",
        scraped_at: new Date().toISOString(),
      },
      {
        company: "Test Company",
        platform: "glassdoor",
        content: "The company culture is okay but could be improved.",
        sentiment_score: 0.1,
        sentiment_label: "neutral",
        sentiment_confidence: 0.7,
        rating: 3,
        author: "Anonymous Employee",
        employment_status: "Current Employee",
        scraped_at: new Date().toISOString(),
      },
    ]

    console.log("🧪 Testing Supabase connection...")

    // Insert test data
    const result = await insertSentimentData(testData)

    console.log("✅ Test data inserted successfully:", result)

    return NextResponse.json({
      success: true,
      message: "Test data inserted successfully",
      insertedRecords: result?.length || 0,
      data: result,
    })
  } catch (error) {
    console.error("❌ Supabase test failed:", error)

    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
        details: "Check your Supabase configuration and environment variables",
      },
      { status: 500 },
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    console.log("🔍 Fetching test data from Supabase...")

    const { searchParams } = new URL(request.url)
    const company = searchParams.get("company")
    const platform = searchParams.get("platform")
    const limit = searchParams.get("limit") ? Number.parseInt(searchParams.get("limit")!) : 10

    const data = await getSentimentData({
      company: company || undefined,
      platform: platform || undefined,
      limit,
    })

    return NextResponse.json({
      success: true,
      message: "Data retrieved successfully",
      count: data?.length || 0,
      data,
    })
  } catch (error) {
    console.error("❌ Failed to fetch data:", error)

    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    )
  }
}
