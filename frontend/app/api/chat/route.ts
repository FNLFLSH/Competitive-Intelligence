import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { message, scrapedData } = await request.json()

    // Simple response based on scraped data
    let response = "I'm here to help analyze your competitive intelligence data."

    if (scrapedData) {
      const { summary, companySentiments } = scrapedData

      if (message.toLowerCase().includes("sentiment")) {
        response = `Based on the scraped data, the average sentiment across ${summary?.companiesAnalyzed || 0} companies is ${Math.round((summary?.averageSentiment || 0) * 100)}%. The data includes ${summary?.totalReviews || 0} total reviews.`
      } else if (message.toLowerCase().includes("companies")) {
        const companies = Object.keys(companySentiments || {})
        response = `I found data for these companies: ${companies.join(", ")}. Which company would you like to know more about?`
      } else if (message.toLowerCase().includes("reviews")) {
        response = `The scraping collected ${summary?.g2Reviews || 0} G2 reviews and ${summary?.glassdoorReviews || 0} Glassdoor reviews, totaling ${summary?.totalReviews || 0} reviews across all platforms.`
      } else {
        response = `I can help you analyze the scraped data from ${summary?.companiesAnalyzed || 0} companies. Ask me about sentiment scores, specific companies, or review breakdowns.`
      }
    } else {
      response = "No scraped data is available yet. Click 'Live Scrape' to generate data I can help you analyze."
    }

    return NextResponse.json({ response })
  } catch (error) {
    console.error("Chat API error:", error)
    return NextResponse.json({ response: "I'm having trouble processing your request right now." }, { status: 500 })
  }
}
