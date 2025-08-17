import { G2Scraper, type G2ScrapingResult } from './g2-scraper';
import { GlassdoorScraper, type GlassdoorScrapingResult } from './glassdoor-scraper';
import { analyzeVaderSentiment, getSentimentLabel } from '../sentiment/vader-sentiment';
import { createClient } from '@supabase/supabase-js';

export interface CompanyReviewData {
  company: string;
  g2Data?: G2ScrapingResult;
  glassdoorData?: GlassdoorScrapingResult;
  overallSentiment: {
    score: number;
    label: string;
    totalReviews: number;
    averageRating: number;
  };
  scrapedAt: Date;
}

export interface SentimentAnalysisResult {
  reviewId: string;
  platform: 'g2' | 'glassdoor';
  company: string;
  content: string;
  rating: number;
  author: string;
  date: string;
  sentiment: {
    score: number;
    label: string;
    compound: number;
    positive: number;
    negative: number;
    neutral: number;
  };
  pros?: string;
  cons?: string;
  helpful: number;
  verified: boolean;
}

export class ReviewScraperManager {
  private g2Scraper: G2Scraper;
  private glassdoorScraper: GlassdoorScraper;
  private supabase: any;

  constructor() {
    this.g2Scraper = new G2Scraper();
    this.glassdoorScraper = new GlassdoorScraper();
    
    // Initialize Supabase client
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
    const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
    this.supabase = createClient(supabaseUrl, supabaseKey);
  }

  async scrapeCompanyReviews(
    companyName: string, 
    g2Url?: string, 
    glassdoorUrl?: string
  ): Promise<CompanyReviewData> {
    const results: CompanyReviewData = {
      company: companyName,
      scrapedAt: new Date(),
      overallSentiment: {
        score: 0,
        label: 'Neutral',
        totalReviews: 0,
        averageRating: 0
      }
    };

    const allSentiments: number[] = [];
    let totalReviews = 0;
    let totalRating = 0;

    // Scrape G2 reviews
    if (g2Url) {
      try {
        console.log(`Scraping G2 reviews for ${companyName}...`);
        results.g2Data = await this.g2Scraper.scrapeReviews(companyName, g2Url);
        
        if (results.g2Data.success && results.g2Data.reviews.length > 0) {
          // Analyze sentiment for each G2 review
          for (const review of results.g2Data.reviews) {
            const sentiment = analyzeVaderSentiment(review.content);
            allSentiments.push(sentiment.score);
            totalReviews++;
            totalRating += review.rating;
          }
        }
      } catch (error) {
        console.error(`Error scraping G2 for ${companyName}:`, error);
      }
    }

    // Scrape Glassdoor reviews
    if (glassdoorUrl) {
      try {
        console.log(`Scraping Glassdoor reviews for ${companyName}...`);
        results.glassdoorData = await this.glassdoorScraper.scrapeReviews(companyName, glassdoorUrl);
        
        if (results.glassdoorData.success && results.glassdoorData.reviews.length > 0) {
          // Analyze sentiment for each Glassdoor review
          for (const review of results.glassdoorData.reviews) {
            const sentiment = analyzeVaderSentiment(review.content);
            allSentiments.push(sentiment.score);
            totalReviews++;
            totalRating += review.rating;
          }
        }
      } catch (error) {
        console.error(`Error scraping Glassdoor for ${companyName}:`, error);
      }
    }

    // Calculate overall sentiment
    if (allSentiments.length > 0) {
      const averageSentiment = allSentiments.reduce((sum, score) => sum + score, 0) / allSentiments.length;
      results.overallSentiment = {
        score: averageSentiment,
        label: getSentimentLabel(averageSentiment),
        totalReviews,
        averageRating: totalReviews > 0 ? totalRating / totalReviews : 0
      };
    }

    return results;
  }

  async saveToSupabase(companyData: CompanyReviewData): Promise<void> {
    try {
      // Save company sentiment summary
      const { error: summaryError } = await this.supabase
        .from('company_sentiment_summary')
        .upsert({
          company: companyData.company,
          overall_sentiment_score: companyData.overallSentiment.score,
          overall_sentiment_label: companyData.overallSentiment.label,
          total_reviews: companyData.overallSentiment.totalReviews,
          average_rating: companyData.overallSentiment.averageRating,
          scraped_at: companyData.scrapedAt.toISOString(),
          g2_url: companyData.g2Data?.url,
          glassdoor_url: companyData.glassdoorData?.url
        });

      if (summaryError) {
        console.error('Error saving company sentiment summary:', summaryError);
      }

      // Save individual reviews with sentiment analysis
      const reviewsToSave: any[] = [];

      // Process G2 reviews
      if (companyData.g2Data?.reviews) {
        for (const review of companyData.g2Data.reviews) {
          const sentiment = analyzeVaderSentiment(review.content);
          reviewsToSave.push({
            review_id: review.id,
            company: companyData.company,
            platform: 'g2',
            content: review.content,
            rating: review.rating,
            author: review.author,
            date: review.date,
            sentiment_score: sentiment.score,
            sentiment_label: getSentimentLabel(sentiment.score),
            sentiment_compound: sentiment.compound,
            sentiment_positive: sentiment.positive,
            sentiment_negative: sentiment.negative,
            sentiment_neutral: sentiment.neutral,
            pros: review.pros,
            cons: review.cons,
            helpful: review.helpful,
            verified: review.verified,
            scraped_at: companyData.scrapedAt.toISOString()
          });
        }
      }

      // Process Glassdoor reviews
      if (companyData.glassdoorData?.reviews) {
        for (const review of companyData.glassdoorData.reviews) {
          const sentiment = analyzeVaderSentiment(review.content);
          reviewsToSave.push({
            review_id: review.id,
            company: companyData.company,
            platform: 'glassdoor',
            content: review.content,
            rating: review.rating,
            author: review.author,
            date: review.date,
            sentiment_score: sentiment.score,
            sentiment_label: getSentimentLabel(sentiment.score),
            sentiment_compound: sentiment.compound,
            sentiment_positive: sentiment.positive,
            sentiment_negative: sentiment.negative,
            sentiment_neutral: sentiment.neutral,
            pros: review.pros,
            cons: review.cons,
            helpful: review.helpful,
            verified: review.verified,
            review_type: review.reviewType,
            scraped_at: companyData.scrapedAt.toISOString()
          });
        }
      }

      // Batch insert reviews
      if (reviewsToSave.length > 0) {
        const { error: reviewsError } = await this.supabase
          .from('company_reviews')
          .upsert(reviewsToSave);

        if (reviewsError) {
          console.error('Error saving reviews:', reviewsError);
        }
      }

      console.log(`Successfully saved data for ${companyData.company}`);
    } catch (error) {
      console.error('Error saving to Supabase:', error);
      throw error;
    }
  }

  async scrapeMultipleCompanies(companies: Array<{
    name: string;
    g2Url?: string;
    glassdoorUrl?: string;
  }>): Promise<CompanyReviewData[]> {
    const results: CompanyReviewData[] = [];

    for (const company of companies) {
      try {
        console.log(`Starting scrape for ${company.name}...`);
        const companyData = await this.scrapeCompanyReviews(
          company.name,
          company.g2Url,
          company.glassdoorUrl
        );

        // Save to Supabase
        await this.saveToSupabase(companyData);
        results.push(companyData);

        // Add delay between companies to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 2000));
      } catch (error) {
        console.error(`Error scraping ${company.name}:`, error);
        // Continue with next company even if one fails
      }
    }

    return results;
  }

  async close(): Promise<void> {
    await this.g2Scraper.close();
    await this.glassdoorScraper.close();
  }
} 