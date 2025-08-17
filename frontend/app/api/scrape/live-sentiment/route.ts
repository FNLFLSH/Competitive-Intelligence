import { NextRequest, NextResponse } from 'next/server';
import { ReviewScraperManager } from '@/lib/scrapers/review-scraper-manager';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { companies } = body;

    if (!companies || !Array.isArray(companies)) {
      return NextResponse.json(
        { error: 'Invalid request: companies array is required' },
        { status: 400 }
      );
    }

    console.log(`Starting live scrape for ${companies.length} companies...`);

    const scraperManager = new ReviewScraperManager();
    
    try {
      const results = await scraperManager.scrapeMultipleCompanies(companies);
      
      // Calculate overall statistics
      const totalCompanies = results.length;
      const successfulCompanies = results.filter(r => 
        (r.g2Data?.success || r.glassdoorData?.success)
      ).length;
      
      const totalReviews = results.reduce((sum, r) => sum + r.overallSentiment.totalReviews, 0);
      const averageSentiment = results.length > 0 
        ? results.reduce((sum, r) => sum + r.overallSentiment.score, 0) / results.length 
        : 0;

      const summary = {
        totalCompanies,
        successfulCompanies,
        totalReviews,
        averageSentiment,
        results: results.map(r => ({
          company: r.company,
          success: r.g2Data?.success || r.glassdoorData?.success,
          totalReviews: r.overallSentiment.totalReviews,
          sentimentScore: r.overallSentiment.score,
          sentimentLabel: r.overallSentiment.label,
          averageRating: r.overallSentiment.averageRating,
          g2Reviews: r.g2Data?.reviews.length || 0,
          glassdoorReviews: r.glassdoorData?.reviews.length || 0
        }))
      };

      return NextResponse.json({
        success: true,
        message: `Successfully scraped ${successfulCompanies}/${totalCompanies} companies`,
        summary,
        results
      });

    } finally {
      await scraperManager.close();
    }

  } catch (error) {
    console.error('Error in live sentiment scraping:', error);
    return NextResponse.json(
      { 
        error: 'Internal server error during scraping',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'Live sentiment scraping endpoint',
    usage: 'POST with companies array containing name, g2Url, and glassdoorUrl'
  });
}

export const dynamic = "force-dynamic"
