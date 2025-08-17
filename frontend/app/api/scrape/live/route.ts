import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Use environment variable for backend URL
    const BACKEND_URL = process.env.SCRAPER_BACKEND_URL?.replace(/\/$/, "") || "http://localhost:8000"

    console.log("🔄 Proxying request to:", `${BACKEND_URL}/api/scrape/live`)

    const response = await fetch(`${BACKEND_URL}/api/scrape/live`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    })

    // Always attempt to read JSON first
    let data: any
    try {
      data = await response.json()
    } catch {
      const text = await response.text()
      data = {
        success: false,
        error: "Backend returned non-JSON response",
        details: text,
        status: response.status,
      }
    }

    return NextResponse.json(data, {
      status: response.ok ? 200 : response.status,
      headers: {
        "Content-Type": "application/json",
      },
    })
  } catch (error) {
    console.error("❌ Proxy error:", error)
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Unknown proxy error",
      },
      {
        status: 500,
        headers: {
          "Content-Type": "application/json",
        },
      },
    )
  }
}
