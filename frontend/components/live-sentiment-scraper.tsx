'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CheckCircle, XCircle, TrendingUp, TrendingDown } from 'lucide-react';

interface Company {
  name: string;
  g2Url?: string;
  glassdoorUrl?: string;
}

interface ScrapingResult {
  company: string;
  success: boolean;
  totalReviews: number;
  sentimentScore: number;
  sentimentLabel: string;
  averageRating: number;
  g2Reviews: number;
  glassdoorReviews: number;
}

interface ScrapingSummary {
  totalCompanies: number;
  successfulCompanies: number;
  totalReviews: number;
  averageSentiment: number;
  results: ScrapingResult[];
}

export function LiveSentimentScraper() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<ScrapingSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  // Load companies from CSV
  useEffect(() => {
    const loadCompanies = async () => {
      try {
        const response = await fetch('/company_review_urls.csv');
        const csvText = await response.text();
        const lines = csvText.split('\n').slice(1); // Skip header
        
        const loadedCompanies: Company[] = [];
        for (const line of lines) {
          if (line.trim()) {
            const [name, g2Url, glassdoorUrl] = line.split(',').map(s => s.trim().replace(/"/g, ''));
            if (name && (g2Url || glassdoorUrl)) {
              loadedCompanies.push({
                name,
                g2Url: g2Url || undefined,
                glassdoorUrl: glassdoorUrl || undefined
              });
            }
          }
        }
        setCompanies(loadedCompanies);
      } catch (error) {
        console.error('Error loading companies:', error);
        setError('Failed to load company data');
      }
    };

    loadCompanies();
  }, []);

  const handleCompanyToggle = (companyName: string) => {
    setSelectedCompanies(prev => 
      prev.includes(companyName)
        ? prev.filter(name => name !== companyName)
        : [...prev, companyName]
    );
  };

  const handleSelectAll = () => {
    setSelectedCompanies(companies.map(c => c.name));
  };

  const handleDeselectAll = () => {
    setSelectedCompanies([]);
  };

  const handleLiveScrape = async () => {
    if (selectedCompanies.length === 0) {
      setError('Please select at least one company to scrape');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults(null);
    setProgress(0);

    try {
      const companiesToScrape = companies.filter(c => selectedCompanies.includes(c.name));
      
      const response = await fetch('/api/scrape/live-sentiment', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          companies: companiesToScrape
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Scraping failed');
      }

      const data = await response.json();
      setResults(data.summary);
      setProgress(100);
    } catch (error) {
      console.error('Scraping error:', error);
      setError(error instanceof Error ? error.message : 'An unknown error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const getSentimentColor = (score: number) => {
    if (score >= 2) return 'text-green-600 bg-green-100';
    if (score >= 0) return 'text-blue-600 bg-blue-100';
    if (score >= -2) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getSentimentIcon = (score: number) => {
    if (score >= 1) return <TrendingUp className="w-4 h-4" />;
    if (score <= -1) return <TrendingDown className="w-4 h-4" />;
    return null;
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Live Sentiment Scraper</CardTitle>
          <CardDescription>
            Select companies to scrape reviews from G2 and Glassdoor with sentiment analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Company Selection */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Select Companies</h3>
              <div className="space-x-2">
                <Button variant="outline" size="sm" onClick={handleSelectAll}>
                  Select All
                </Button>
                <Button variant="outline" size="sm" onClick={handleDeselectAll}>
                  Deselect All
                </Button>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-60 overflow-y-auto">
              {companies.map((company) => (
                <div
                  key={company.name}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedCompanies.includes(company.name)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleCompanyToggle(company.name)}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm">{company.name}</span>
                    <div className="flex space-x-1">
                      {company.g2Url && (
                        <Badge variant="secondary" className="text-xs">G2</Badge>
                      )}
                      {company.glassdoorUrl && (
                        <Badge variant="secondary" className="text-xs">Glassdoor</Badge>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              {selectedCompanies.length} companies selected
            </div>
            <Button
              onClick={handleLiveScrape}
              disabled={isLoading || selectedCompanies.length === 0}
              className="min-w-[120px]"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Scraping...
                </>
              ) : (
                'Live Scrape'
              )}
            </Button>
          </div>

          {/* Progress */}
          {isLoading && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Scraping in progress...</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} className="w-full" />
            </div>
          )}

          {/* Error Display */}
          {error && (
            <Alert variant="destructive">
              <XCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Results Display */}
          {results && (
            <div className="space-y-4">
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Successfully scraped {results.successfulCompanies}/{results.totalCompanies} companies
                  with {results.totalReviews} total reviews
                </AlertDescription>
              </Alert>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{results.totalCompanies}</div>
                    <div className="text-sm text-gray-600">Total Companies</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-green-600">{results.successfulCompanies}</div>
                    <div className="text-sm text-gray-600">Successful</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{results.totalReviews}</div>
                    <div className="text-sm text-gray-600">Total Reviews</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold">{results.averageSentiment.toFixed(2)}</div>
                    <div className="text-sm text-gray-600">Avg Sentiment</div>
                  </CardContent>
                </Card>
              </div>

              {/* Detailed Results */}
              <div className="space-y-2">
                <h3 className="text-lg font-semibold">Company Results</h3>
                <div className="space-y-2">
                  {results.results.map((result) => (
                    <Card key={result.company}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">{result.company}</span>
                            {result.success ? (
                              <CheckCircle className="w-4 h-4 text-green-600" />
                            ) : (
                              <XCircle className="w-4 h-4 text-red-600" />
                            )}
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={getSentimentColor(result.sentimentScore)}>
                              {getSentimentIcon(result.sentimentScore)}
                              {result.sentimentScore.toFixed(2)}
                            </Badge>
                            <Badge variant="outline">
                              {result.totalReviews} reviews
                            </Badge>
                          </div>
                        </div>
                        <div className="mt-2 text-sm text-gray-600">
                          {result.g2Reviews} G2 reviews • {result.glassdoorReviews} Glassdoor reviews
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
