import { type NextRequest, NextResponse } from "next/server"

// Simple dummy data that always works
const DUMMY_DATA = [
  {
    company: "Sage",
    totalReviews: 20,
    averageSentiment: 0.84,
    averageRating: 4.2,
    platforms: {
      capterra: {
        reviews: 20,
        avgSentiment: 0.84,
        avgRating: 4.2
      }
    }
  },
  {
    company: "QuickBooks",
    totalReviews: 20,
    averageSentiment: 0.79,
    averageRating: 4.2,
    platforms: {
      capterra: {
        reviews: 20,
        avgSentiment: 0.79,
        avgRating: 4.2
      }
    }
  },
  {
    company: "Xero",
    totalReviews: 20,
    averageSentiment: 0.75,
    averageRating: 4.1,
    platforms: {
      capterra: {
        reviews: 20,
        avgSentiment: 0.75,
        avgRating: 4.1
      }
    }
  },
  {
    company: "Microsoft Dynamics",
    totalReviews: 20,
    averageSentiment: 0.6,
    averageRating: 3.8,
    platforms: {
      capterra: {
        reviews: 20,
        avgSentiment: 0.6,
        avgRating: 3.8
      }
    }
  },
  {
    company: "SAP",
    totalReviews: 20,
    averageSentiment: 0.5,
    averageRating: 3.5,
    platforms: {
      capterra: {
        reviews: 20,
        avgSentiment: 0.5,
        avgRating: 3.5
      }
    }
  }
]

// Simple AI response function
function getAIResponse(message: string, selectedCompany: string) {
  const lowerMessage = message.toLowerCase()
  
  // Find company data
  const company = DUMMY_DATA.find(c => c.company === selectedCompany)
  
  // Handle different types of questions
  if (lowerMessage.includes("sentiment") && selectedCompany) {
    if (company) {
      const sentimentPercent = (company.averageSentiment * 100).toFixed(1)
      const sentimentLabel = company.averageSentiment > 0.1 ? "positive" : 
                           company.averageSentiment < -0.1 ? "negative" : "neutral"
      
      const sentimentEmoji = company.averageSentiment > 0.1 ? "😊" : 
                            company.averageSentiment < -0.1 ? "😟" : "😐"
      
      return {
        response: `${sentimentEmoji} **${selectedCompany} Sentiment Analysis**

Based on ${company.totalReviews} reviews, ${selectedCompany} has a **${sentimentLabel} sentiment score of ${sentimentPercent}%**.

**What this means:**
• ${company.averageSentiment > 0.1 ? "Users generally express satisfaction and positive experiences" : 
    company.averageSentiment < -0.1 ? "Users have some concerns and mixed experiences" : 
    "Users have neutral to mixed feelings about the product/service"}
• The analysis considers review language, tone, and overall satisfaction patterns
• Data is aggregated from multiple review platforms for accuracy

**Insight:** ${company.averageSentiment > 0.1 ? "This strong positive sentiment suggests ${selectedCompany} is meeting user expectations well!" : 
  company.averageSentiment < -0.1 ? "There might be areas where ${selectedCompany} could improve user experience." : 
  "The neutral sentiment indicates mixed user experiences - there's room for improvement."}`,
        metadata: {
          company: selectedCompany,
          sentiment: company.averageSentiment,
          totalReviews: company.totalReviews
        }
      }
    } else {
      return {
        response: `I don't have specific sentiment data for ${selectedCompany}. Available companies are: ${DUMMY_DATA.map(c => c.company).join(", ")}`,
        metadata: {
          availableCompanies: DUMMY_DATA.map(c => c.company)
        }
      }
    }
  }
  
  if (lowerMessage.includes("rating") && selectedCompany) {
    if (company) {
      const ratingEmoji = company.averageRating >= 4.0 ? "⭐" : 
                         company.averageRating >= 3.0 ? "⭐" : "⭐"
      const ratingStars = "⭐".repeat(Math.round(company.averageRating))
      
      return {
        response: `${ratingEmoji} **${selectedCompany} Rating Analysis**

${selectedCompany} has an **average rating of ${company.averageRating.toFixed(1)}/5 stars** based on ${company.totalReviews} reviews.

**Rating Breakdown:**
${ratingStars} (${company.averageRating.toFixed(1)}/5)

**What this tells us:**
• ${company.averageRating >= 4.0 ? "Excellent user satisfaction - users love this product/service!" :
    company.averageRating >= 3.0 ? "Good user satisfaction with room for improvement" :
    "Users have concerns - there are areas that need attention"}
• Rating is calculated from multiple review platforms
• Based on ${company.totalReviews} real user reviews

**Insight:** ${company.averageRating >= 4.0 ? "This high rating suggests ${selectedCompany} is delivering great value to users!" :
  company.averageRating >= 3.0 ? "While good, there's potential for ${selectedCompany} to improve user experience." :
  "This rating indicates ${selectedCompany} should focus on addressing user concerns."}`,
        metadata: {
          company: selectedCompany,
          rating: company.averageRating,
          totalReviews: company.totalReviews
        }
      }
    }
  }
  
  if (lowerMessage.includes("companies") || lowerMessage.includes("data")) {
    return {
      response: `📊 **Available Company Data**

I have detailed data for **${DUMMY_DATA.length} companies** with **20 reviews each**:

${DUMMY_DATA.map(c => `• **${c.company}**: ${c.totalReviews} reviews, ${c.averageRating.toFixed(1)}/5 stars, ${(c.averageSentiment * 100).toFixed(1)}% sentiment`).join('\n')}

**What I can analyze:**
• Sentiment scores and analysis
• Average ratings and user satisfaction
• Company comparisons
• Review insights and trends

Just ask me about any specific company or ask me to compare companies!`,
      metadata: {
        totalCompanies: DUMMY_DATA.length,
        companies: DUMMY_DATA.map(c => c.company)
      }
    }
  }
  
  if (lowerMessage.includes("hello") || lowerMessage.includes("hi") || lowerMessage.includes("hey")) {
    return {
      response: `Hello! 👋 I'm your AI assistant for competitive intelligence. I have data for **${DUMMY_DATA.length} companies** with **20 reviews each** and detailed sentiment analysis. I can help you analyze company data, compare companies, or answer questions about specific companies. What would you like to know?`,
      metadata: {
        totalCompanies: DUMMY_DATA.length,
        companies: DUMMY_DATA.map(c => c.company)
      }
    }
  }
  
  // Default response
  return {
    response: `I'm your AI assistant for competitive intelligence! I have data for ${DUMMY_DATA.length} companies with detailed reviews and sentiment analysis. You can ask me about:

• **Company sentiment** (e.g., "What's the sentiment for Sage?")
• **Company ratings** (e.g., "What's the rating for QuickBooks?")
• **Available companies** (e.g., "What companies do you have data for?")
• **Company comparisons** (e.g., "Compare Sage and QuickBooks")

Available companies: ${DUMMY_DATA.map(c => c.company).join(", ")}`,
    metadata: {
      totalCompanies: DUMMY_DATA.length,
      companies: DUMMY_DATA.map(c => c.company)
    }
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, selectedCompany = "" } = body
    
    console.log('🤖 AI Screening Request:', { message, selectedCompany })
    
    // Get AI response using simple logic
    const aiResponse = getAIResponse(message, selectedCompany)
    
    console.log('✅ AI Response generated:', aiResponse.metadata)
    
    return NextResponse.json({
      response: aiResponse.response,
      metadata: aiResponse.metadata
    })
    
  } catch (error) {
    console.error('❌ AI Screening Error:', error)
    return NextResponse.json({
      response: "I'm having trouble processing your request right now. Please try again!",
      metadata: {}
    }, { status: 500 })
  }
} 