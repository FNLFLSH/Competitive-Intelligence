// VADER (Valence Aware Dictionary and sEntiment Reasoner) Sentiment Analysis
// Implementation based on the VADER lexicon and scoring algorithm

interface VaderSentimentResult {
  compound: number; // Normalized score between -1 and 1
  positive: number;
  negative: number;
  neutral: number;
  score: number; // Our custom score from -4 to +4
}

// VADER Lexicon (simplified version - you can expand this)
const VADER_LEXICON: Record<string, number> = {
  // Positive words
  'good': 1.9, 'great': 3.1, 'excellent': 3.3, 'amazing': 3.1, 'wonderful': 3.0,
  'fantastic': 3.0, 'perfect': 3.3, 'outstanding': 3.2, 'brilliant': 3.0, 'superb': 3.2,
  'awesome': 2.8, 'incredible': 3.0, 'terrific': 2.8, 'fabulous': 2.8, 'marvelous': 3.0,
  'love': 3.1, 'like': 1.8, 'enjoy': 2.0, 'appreciate': 2.2, 'adore': 3.0,
  'best': 2.8, 'better': 1.8, 'improved': 2.0, 'upgrade': 1.8, 'enhanced': 2.2,
  'easy': 1.8, 'simple': 1.6, 'intuitive': 2.2, 'user-friendly': 2.4, 'convenient': 2.0,
  'fast': 2.0, 'quick': 1.8, 'efficient': 2.2, 'reliable': 2.4, 'stable': 2.0,
  'helpful': 2.2, 'useful': 2.0, 'valuable': 2.4, 'beneficial': 2.2, 'effective': 2.2,
  
  // Negative words
  'bad': -1.8, 'terrible': -3.0, 'awful': -3.0, 'horrible': -3.0, 'dreadful': -3.0,
  'worst': -3.0, 'worse': -2.0, 'poor': -2.0, 'disappointing': -2.4, 'frustrating': -2.4,
  'annoying': -2.2, 'irritating': -2.4, 'maddening': -3.0, 'infuriating': -3.0, 'rage': -3.0,
  'hate': -3.0, 'dislike': -2.0, 'loathe': -3.0, 'despise': -3.0, 'abhor': -3.0,
  'difficult': -1.8, 'hard': -1.6, 'complex': -1.8, 'complicated': -2.0, 'confusing': -2.2,
  'slow': -1.8, 'laggy': -2.2, 'buggy': -2.4, 'unreliable': -2.4, 'unstable': -2.2,
  'useless': -2.4, 'worthless': -2.8, 'pointless': -2.4, 'broken': -2.4, 'defective': -2.4,
  'expensive': -1.6, 'costly': -1.8, 'overpriced': -2.2, 'waste': -2.0, 'rip-off': -2.8,
  
  // Neutral words (context dependent)
  'okay': 0.5, 'fine': 0.5, 'decent': 0.8, 'average': 0.0, 'normal': 0.0,
  'standard': 0.0, 'basic': 0.0, 'simple': 0.0, 'straightforward': 0.5,
  
  // Intensifiers
  'very': 0.293, 'really': 0.293, 'extremely': 0.293, 'incredibly': 0.293,
  'completely': 0.293, 'totally': 0.293, 'absolutely': 0.293, 'definitely': 0.293,
  
  // Negation words
  'not': -0.74, 'no': -0.74, 'never': -0.74, 'none': -0.74, 'nobody': -0.74,
  'nothing': -0.74, 'neither': -0.74, 'nowhere': -0.74, 'hardly': -0.74,
  'barely': -0.74, 'scarcely': -0.74, 'doesn\'t': -0.74, 'isn\'t': -0.74,
  'wasn\'t': -0.74, 'shouldn\'t': -0.74, 'wouldn\'t': -0.74, 'couldn\'t': -0.74,
  'won\'t': -0.74, 'can\'t': -0.74, 'don\'t': -0.74
};

// Booster words that intensify sentiment
const BOOSTER_DICT: Record<string, number> = {
  'very': 0.293, 'really': 0.293, 'extremely': 0.293, 'incredibly': 0.293,
  'completely': 0.293, 'totally': 0.293, 'absolutely': 0.293, 'definitely': 0.293,
  'highly': 0.293, 'thoroughly': 0.293, 'entirely': 0.293, 'fully': 0.293,
  'quite': 0.293, 'rather': 0.293, 'pretty': 0.293, 'fairly': 0.293,
  'somewhat': 0.293, 'slightly': 0.293, 'barely': 0.293, 'hardly': 0.293
};

// Negation words
const NEGATE: Set<string> = new Set([
  'not', 'no', 'never', 'none', 'nobody', 'nothing', 'neither', 'nowhere', 'hardly',
  'barely', 'scarcely', 'doesn\'t', 'isn\'t', 'wasn\'t', 'shouldn\'t', 'wouldn\'t',
  'couldn\'t', 'won\'t', 'can\'t', 'don\'t'
]);

export function analyzeVaderSentiment(text: string): VaderSentimentResult {
  const words = text.toLowerCase().split(/\s+/);
  const sentiments: number[] = [];
  const itemIntensity = 0.293;
  
  let i = 0;
  while (i < words.length) {
    const word = words[i];
    let valence = 0;
    
    // Check if word is in lexicon
    if (VADER_LEXICON[word]) {
      valence = VADER_LEXICON[word];
      
      // Check for negation
      if (i > 0 && NEGATE.has(words[i - 1])) {
        valence = valence * -1;
      }
      
      // Check for booster words
      if (i > 0 && BOOSTER_DICT[words[i - 1]]) {
        valence = valence * (1 + BOOSTER_DICT[words[i - 1]]);
      }
      if (i < words.length - 1 && BOOSTER_DICT[words[i + 1]]) {
        valence = valence * (1 + BOOSTER_DICT[words[i + 1]]);
      }
      
      sentiments.push(valence);
    }
    
    i++;
  }
  
  if (sentiments.length === 0) {
    return {
      compound: 0,
      positive: 0,
      negative: 0,
      neutral: 1,
      score: 0
    };
  }
  
  // Calculate scores
  const sum = sentiments.reduce((a, b) => a + b, 0);
  const mean = sum / sentiments.length;
  
  // Normalize compound score
  const compound = Math.tanh(mean) * 0.5 + 0.5; // Convert to 0-1 range
  
  // Count positive, negative, neutral
  const positive = sentiments.filter(s => s > 0).length;
  const negative = sentiments.filter(s => s < 0).length;
  const neutral = sentiments.filter(s => s === 0).length;
  
  // Convert to our custom -4 to +4 scale
  const score = (compound - 0.5) * 8; // Convert 0-1 to -4 to +4
  
  return {
    compound,
    positive,
    negative,
    neutral,
    score: Math.max(-4, Math.min(4, score)) // Clamp to -4 to +4
  };
}

export function getSentimentLabel(score: number): string {
  if (score >= 3) return 'Very Positive';
  if (score >= 1) return 'Positive';
  if (score >= -1) return 'Neutral';
  if (score >= -3) return 'Negative';
  return 'Very Negative';
}

export function analyzeReviewSentiment(review: { content: string; pros?: string; cons?: string }): {
  overall: VaderSentimentResult;
  pros?: VaderSentimentResult;
  cons?: VaderSentimentResult;
} {
  const overall = analyzeVaderSentiment(review.content);
  const pros = review.pros ? analyzeVaderSentiment(review.pros) : undefined;
  const cons = review.cons ? analyzeVaderSentiment(review.cons) : undefined;
  
  return { overall, pros, cons };
}
