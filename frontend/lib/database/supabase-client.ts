import { createClient } from "@supabase/supabase-js"

// Public client for client-side operations
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error("Missing Supabase environment variables")
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Admin client for server-side operations (bypasses RLS)
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY

export const supabaseAdmin = supabaseServiceKey
  ? createClient(supabaseUrl, supabaseServiceKey, {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
    })
  : null

// Types for our sentiment_data table
export interface SentimentData {
  id?: number
  company: string
  platform: string
  title?: string
  content: string
  author?: string
  url?: string
  sentiment_score?: number
  sentiment_label?: "positive" | "negative" | "neutral"
  sentiment_confidence?: number
  rating?: number
  pros?: string[]
  cons?: string[]
  reviewer_role?: string
  company_size?: string
  employment_status?: string
  recommendation?: boolean
  review_date?: string
  scraped_at?: string
  created_at?: string
  updated_at?: string
  raw_data?: any
}

// Helper functions for database operations
export async function insertSentimentData(data: SentimentData[]) {
  if (!supabaseAdmin) {
    throw new Error("Supabase admin client not configured")
  }

  const { data: result, error } = await supabaseAdmin.from("sentiment_data").insert(data).select()

  if (error) {
    console.error("Error inserting sentiment data:", error)
    throw error
  }

  return result
}

export async function getSentimentData(company?: string, platform?: string, limit = 100) {
  let query = supabase.from("sentiment_data").select("*").order("scraped_at", { ascending: false }).limit(limit)

  if (company) {
    query = query.ilike("company", `%${company}%`)
  }

  if (platform) {
    query = query.eq("platform", platform)
  }

  const { data, error } = await query

  if (error) {
    console.error("Error fetching sentiment data:", error)
    throw error
  }

  return data
}

export async function getCompanySentimentSummary(company: string) {
  const { data, error } = await supabase
    .from("sentiment_data")
    .select("sentiment_score, rating, platform")
    .ilike("company", `%${company}%`)
    .not("sentiment_score", "is", null)

  if (error) {
    console.error("Error fetching company sentiment summary:", error)
    throw error
  }

  if (!data || data.length === 0) {
    return null
  }

  // Calculate averages
  const totalReviews = data.length
  const avgSentiment = data.reduce((sum, item) => sum + (item.sentiment_score || 0), 0) / totalReviews
  const avgRating =
    data.filter((item) => item.rating).reduce((sum, item) => sum + (item.rating || 0), 0) /
    data.filter((item) => item.rating).length

  // Platform breakdown
  const platformBreakdown = data.reduce(
    (acc, item) => {
      acc[item.platform] = (acc[item.platform] || 0) + 1
      return acc
    },
    {} as Record<string, number>,
  )

  return {
    totalReviews,
    avgSentiment,
    avgRating: avgRating || 0,
    platformBreakdown,
  }
}
