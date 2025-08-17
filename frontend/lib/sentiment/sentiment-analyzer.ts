import type { ScrapedPost, ScrapedComment } from "../scrapers/base-scraper"
import { analyzeVaderSentiment } from "./vader-sentiment"

export interface SentimentResult {
  score: number // -1 to 1 range
  label: "positive" | "negative" | "neutral"
  confidence: number // 0 to 1 range
}

export function analyzeSentiment(text: string): SentimentResult {
  // Use VADER sentiment analysis
  return analyzeVaderSentiment(text)
}

export function categorizeSentiment(score: number): "positive" | "negative" | "neutral" {
  if (score > 0.1) return "positive"
  if (score < -0.1) return "negative"
  return "neutral"
}

export function normalizeSentimentScore(score: number): number {
  // Convert -1 to 1 range to 0 to 100 range
  return Math.round(((score + 1) / 2) * 100)
}

export class SentimentAnalyzer {
  private positiveWords = [
    "excellent",
    "amazing",
    "great",
    "awesome",
    "fantastic",
    "wonderful",
    "love",
    "perfect",
    "best",
    "outstanding",
    "brilliant",
    "superb",
    "recommend",
    "helpful",
    "easy",
    "simple",
    "efficient",
    "reliable",
    "fast",
    "quick",
    "smooth",
    "intuitive",
    "user-friendly",
    "powerful",
  ]

  private negativeWords = [
    "terrible",
    "awful",
    "horrible",
    "bad",
    "worst",
    "hate",
    "broken",
    "buggy",
    "slow",
    "confusing",
    "complicated",
    "difficult",
    "expensive",
    "overpriced",
    "useless",
    "frustrating",
    "annoying",
    "crash",
    "error",
    "problem",
    "issue",
    "fail",
    "disappointing",
  ]

  private intensifiers = [
    "very",
    "extremely",
    "really",
    "absolutely",
    "completely",
    "totally",
    "incredibly",
    "amazingly",
    "exceptionally",
    "particularly",
    "especially",
  ]

  private negators = [
    "not",
    "no",
    "never",
    "nothing",
    "nobody",
    "nowhere",
    "neither",
    "nor",
    "none",
    "without",
    "barely",
    "hardly",
    "scarcely",
  ]

  analyzeSentiment(text: string): SentimentResult {
    const words = this.tokenize(text.toLowerCase())
    let score = 0
    let magnitude = 0
    let wordCount = 0

    for (let i = 0; i < words.length; i++) {
      const word = words[i]
      let wordScore = 0

      // Check if word is positive or negative
      if (this.positiveWords.includes(word)) {
        wordScore = 1
      } else if (this.negativeWords.includes(word)) {
        wordScore = -1
      }

      if (wordScore !== 0) {
        // Check for intensifiers before the word
        if (i > 0 && this.intensifiers.includes(words[i - 1])) {
          wordScore *= 1.5
        }

        // Check for negators before the word
        if (i > 0 && this.negators.includes(words[i - 1])) {
          wordScore *= -1
        }

        score += wordScore
        magnitude += Math.abs(wordScore)
        wordCount++
      }
    }

    // Normalize scores
    const normalizedScore = wordCount > 0 ? score / wordCount : 0
    const normalizedMagnitude = wordCount > 0 ? magnitude / wordCount : 0

    // Determine label and confidence
    const label: "positive" | "negative" | "neutral" = categorizeSentiment(normalizedScore)
    const confidence: number = Math.max(0, Math.min(1, Math.abs(normalizedScore)))

    return {
      score: Math.max(-1, Math.min(1, normalizedScore)),
      magnitude: Math.max(0, Math.min(1, normalizedMagnitude)),
      label,
      confidence,
    }
  }

  analyzePost(post: ScrapedPost): ScrapedPost {
    const sentiment = analyzeSentiment(post.content)

    // Convert sentiment score to 0-100 scale for dashboard
    const sentimentScore = normalizeSentimentScore(sentiment.score)

    return {
      ...post,
      sentiment: sentimentScore,
    }
  }

  analyzeComment(comment: ScrapedComment): ScrapedComment {
    const sentiment = analyzeSentiment(comment.content)
    const sentimentScore = normalizeSentimentScore(sentiment.score)

    const analyzedComment = {
      ...comment,
      sentiment: sentimentScore,
    }

    // Recursively analyze replies
    if (comment.replies) {
      analyzedComment.replies = comment.replies.map((reply) => this.analyzeComment(reply))
    }

    return analyzedComment
  }

  private tokenize(text: string): string[] {
    return text
      .replace(/[^\w\s]/g, " ")
      .split(/\s+/)
      .filter((word) => word.length > 0)
  }

  // Batch analyze multiple posts
  analyzePosts(posts: ScrapedPost[]): ScrapedPost[] {
    return posts.map((post) => this.analyzePost(post))
  }

  // Calculate aggregate sentiment for a company
  calculateCompanySentiment(posts: ScrapedPost[]): {
    averageSentiment: number
    totalMentions: number
    positiveCount: number
    negativeCount: number
    neutralCount: number
  } {
    if (posts.length === 0) {
      return {
        averageSentiment: 50,
        totalMentions: 0,
        positiveCount: 0,
        negativeCount: 0,
        neutralCount: 0,
      }
    }

    let totalSentiment = 0
    let positiveCount = 0
    let negativeCount = 0
    let neutralCount = 0

    posts.forEach((post) => {
      if (post.sentiment !== undefined) {
        totalSentiment += post.sentiment

        if (post.sentiment > 60) {
          positiveCount++
        } else if (post.sentiment < 40) {
          negativeCount++
        } else {
          neutralCount++
        }
      }
    })

    return {
      averageSentiment: Math.round(totalSentiment / posts.length),
      totalMentions: posts.length,
      positiveCount,
      negativeCount,
      neutralCount,
    }
  }
}
