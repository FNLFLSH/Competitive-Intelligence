// Test script for the review scraping system
// Run with: node test-scraping.js

const { ReviewScraperManager } = require('./lib/scrapers/review-scraper-manager');

async function testScraping() {
  console.log('🧪 Testing Review Scraping System...\n');

  const manager = new ReviewScraperManager();

  try {
    // Test with a single company
    const testCompany = {
      name: 'Access Group',
      g2Url: 'https://www.g2.com/products/access-peoplehr/reviews#reviews',
      glassdoorUrl: 'https://www.glassdoor.com/Reviews/The-Access-Group-UK-Reviews-E913550.htm'
    };

    console.log('📊 Testing single company scrape...');
    const result = await manager.scrapeCompanyReviews(
      testCompany.name,
      testCompany.g2Url,
      testCompany.glassdoorUrl
    );

    console.log('✅ Scraping completed!');
    console.log('📈 Results:');
    console.log(`   Company: ${result.company}`);
    console.log(`   Total Reviews: ${result.overallSentiment.totalReviews}`);
    console.log(`   Sentiment Score: ${result.overallSentiment.score.toFixed(2)}`);
    console.log(`   Sentiment Label: ${result.overallSentiment.label}`);
    console.log(`   Average Rating: ${result.overallSentiment.averageRating.toFixed(2)}`);
    
    if (result.g2Data) {
      console.log(`   G2 Reviews: ${result.g2Data.reviews.length}`);
    }
    
    if (result.glassdoorData) {
      console.log(`   Glassdoor Reviews: ${result.glassdoorData.reviews.length}`);
    }

    // Test sentiment analysis
    console.log('\n🧠 Testing sentiment analysis...');
    const { analyzeVaderSentiment, getSentimentLabel } = require('./lib/sentiment/vader-sentiment');
    
    const testTexts = [
      'This product is absolutely amazing and works perfectly!',
      'Terrible experience, would not recommend to anyone.',
      'It\'s okay, nothing special but gets the job done.'
    ];

    testTexts.forEach((text, index) => {
      const sentiment = analyzeVaderSentiment(text);
      console.log(`   Test ${index + 1}: "${text}"`);
      console.log(`      Score: ${sentiment.score.toFixed(2)}`);
      console.log(`      Label: ${getSentimentLabel(sentiment.score)}`);
    });

    console.log('\n✅ All tests passed!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('Stack trace:', error.stack);
  } finally {
    await manager.close();
  }
}

// Run the test
testScraping().catch(console.error); 