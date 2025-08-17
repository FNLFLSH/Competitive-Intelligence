"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import {
  TrendingUp,
  AlertTriangle,
  Users,
  MessageSquare,
  BarChart3,
  Bell,
  Filter,
  Search,
  Download,
  RefreshCw,
  Target,
  Briefcase,
  Zap,
  Eye,
  CheckCircle,
  XCircle,
  Activity,
  Play,
  Loader2,
  Check,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { ChatWidget } from "@/components/chat-widget"
import { AIScreeningChat } from "@/components/ai-screening-chat"
import { ThemeToggle } from "@/components/theme-toggle"
import Link from "next/link"

export default function IntelligenceDashboard() {
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([])
  const [timeRange, setTimeRange] = useState("7d")
  const [selectedSource, setSelectedSource] = useState("all")
  const [selectedSources, setSelectedSources] = useState<string[]>(["g2", "glassdoor", "capterra"])
  const [isScrapingTest, setIsScrapingTest] = useState(false)
  const [scrapingResults, setScrapingResults] = useState<any>(null)
  const [open, setOpen] = useState(false)
  const [competitorsData, setCompetitorsData] = useState<any[]>([])
  const [selectedJobCompany, setSelectedJobCompany] = useState<string | null>(null)
  const [showJobDetails, setShowJobDetails] = useState(false)

  // Company data from CSV - companies with actual Capterra URLs
  const companyData = [
    "Sage",
    "Intuit",
    "Xero",
    "Oracle NetSuite",
    "Microsoft Dynamics",
    "SAP",
    "Workday",
    "Bill.com",
    "ADP",
    "Acumatica",
    "Cegid",
    "DATEV",
    "Haufe",
    "IRIS",
    "Jonas Construction",
    "Trimble/Viewpoint",
    "SumUp",
    "Square",
    "Yooz",
    "Emburse",
    "Rippling",
    "Wolters Kluwer",
    "Iplicit",
    "Oracle",
    "Moss",
    "Strada",
    "FastBill",
    "BrightPay",
    "Access Group",
    "Grupo Primavera",
    "Holded",
  ]

  // Filter companies based on selection
  const getFilteredCompanies = () => {
    if (selectedCompanies.length === 0) {
      return companyData
    }
    return selectedCompanies
  }

  // Use real data if available from scraping results, show ALL companies
  const competitors = competitorsData.length > 0 ? competitorsData.map((comp) => {
    const isUs = comp.name === "Sage"
    const realData = scrapingResults?.companySentiments?.[comp.name.toLowerCase()]

    return {
      name: comp.name,
      sentiment: realData?.averageSentiment || comp.sentiment,
      change: "N/A",
      volume: realData?.totalReviews || comp.volume,
      isUs,
      realData: !!realData || comp.realData,
      sources: {
        x: comp.sources.x,
        reddit: comp.sources.reddit,
        g2: typeof realData?.platforms?.g2 === 'object' ? realData.platforms.g2.reviews : (realData?.platforms?.g2 || comp.sources.g2),
        youtube: comp.sources.youtube,
        glassdoor: typeof realData?.platforms?.glassdoor === 'object' ? realData.platforms.glassdoor.reviews : (realData?.platforms?.glassdoor || comp.sources.glassdoor),
        capterra: typeof realData?.platforms?.capterra === 'object' ? realData.platforms.capterra.reviews : (realData?.platforms?.capterra || comp.sources.capterra),
      },
    }
  }) : []

  // Filter competitors based on selection
  const filteredCompetitors = selectedCompanies.length === 0 
    ? competitors 
    : selectedCompanies.map(companyName => {
        // Find existing competitor data
        const existingCompetitor = competitors.find(comp => comp.name === companyName)
        
        if (existingCompetitor) {
          return existingCompetitor
        }
        
        // Create new competitor entry for selected company
        return {
          name: companyName,
          sentiment: "N/A",
          change: "N/A",
          volume: "N/A",
          isUs: companyName === "Sage",
          realData: false,
          sources: {
            x: "N/A",
            reddit: "N/A",
            g2: "N/A",
            youtube: "N/A",
            glassdoor: "N/A",
            capterra: "N/A"
          }
        }
      })

  const alerts = [
    {
      type: "info",
      message: scrapingResults
        ? "Live data successfully scraped from G2 and Glassdoor"
        : "No active alerts - start scraping to generate insights",
      time: scrapingResults ? "Just now" : "N/A",
      priority: scrapingResults ? "high" : "low",
      source: scrapingResults ? "live-scraper" : "system",
    },
  ]

  const hiringTrends = [
    {
      company: "Sage",
      role: "Senior Software Engineer",
      location: "Newcastle, UK",
      count: "12",
      change: "+3 this week"
    },
    {
      company: "Intuit",
      role: "Product Manager",
      location: "Mountain View, CA",
      count: "8",
      change: "+2 this week"
    },
    {
      company: "Xero",
      role: "UX Designer",
      location: "Wellington, NZ",
      count: "5",
      change: "+1 this week"
    },
    {
      company: "Oracle NetSuite",
      role: "Cloud Solutions Architect",
      location: "Austin, TX",
      count: "15",
      change: "+4 this week"
    },
    {
      company: "Microsoft Dynamics",
      role: "AI/ML Engineer",
      location: "Redmond, WA",
      count: "22",
      change: "+6 this week"
    },
    {
      company: "Workday",
      role: "Data Scientist",
      location: "Pleasanton, CA",
      count: "9",
      change: "+2 this week"
    },
    {
      company: "Bill.com",
      role: "Frontend Developer",
      location: "San Jose, CA",
      count: "7",
      change: "+1 this week"
    },
    {
      company: "ADP",
      role: "DevOps Engineer",
      location: "Roseland, NJ",
      count: "11",
      change: "+3 this week"
    }
  ]

  // Detailed job listings for each company
  const detailedJobListings = {
    "Sage": [
      {
        id: "sage-1",
        title: "Senior Software Engineer",
        location: "Newcastle, UK",
        type: "Full-time",
        salary: "£65,000 - £85,000",
        posted: "2 days ago",
        description: "Join our core product team to build scalable cloud solutions for accounting software.",
        requirements: ["React", "Node.js", "AWS", "5+ years experience"],
        benefits: ["Remote work", "Health insurance", "25 days holiday"]
      },
      {
        id: "sage-2",
        title: "Product Manager",
        location: "London, UK",
        type: "Full-time",
        salary: "£70,000 - £90,000",
        posted: "1 week ago",
        description: "Lead product strategy for Sage's cloud accounting platform.",
        requirements: ["Product management", "Agile", "3+ years experience"],
        benefits: ["Flexible hours", "Stock options", "Learning budget"]
      },
      {
        id: "sage-3",
        title: "DevOps Engineer",
        location: "Manchester, UK",
        type: "Full-time",
        salary: "£60,000 - £80,000",
        posted: "3 days ago",
        description: "Build and maintain cloud infrastructure for our global platform.",
        requirements: ["Docker", "Kubernetes", "Azure", "3+ years experience"],
        benefits: ["Remote work", "Health insurance", "Conference budget"]
      }
    ],
    "Intuit": [
      {
        id: "intuit-1",
        title: "Product Manager",
        location: "Mountain View, CA",
        type: "Full-time",
        salary: "$140,000 - $180,000",
        posted: "2 days ago",
        description: "Drive product strategy for QuickBooks Online platform.",
        requirements: ["Product management", "SaaS", "5+ years experience"],
        benefits: ["Stock options", "Health insurance", "401k matching"]
      },
      {
        id: "intuit-2",
        title: "Senior Frontend Engineer",
        location: "San Diego, CA",
        type: "Full-time",
        salary: "$130,000 - $170,000",
        posted: "1 week ago",
        description: "Build modern React applications for financial software.",
        requirements: ["React", "TypeScript", "4+ years experience"],
        benefits: ["Remote work", "Health insurance", "Learning budget"]
      }
    ],
    "Xero": [
      {
        id: "xero-1",
        title: "UX Designer",
        location: "Wellington, NZ",
        type: "Full-time",
        salary: "NZ$90,000 - NZ$120,000",
        posted: "3 days ago",
        description: "Design intuitive user experiences for accounting software.",
        requirements: ["Figma", "User research", "3+ years experience"],
        benefits: ["Remote work", "Health insurance", "Flexible hours"]
      },
      {
        id: "xero-2",
        title: "Backend Engineer",
        location: "Auckland, NZ",
        type: "Full-time",
        salary: "NZ$100,000 - NZ$130,000",
        posted: "1 week ago",
        description: "Build scalable APIs for cloud accounting platform.",
        requirements: ["Python", "Django", "AWS", "4+ years experience"],
        benefits: ["Stock options", "Health insurance", "Conference budget"]
      }
    ],
    "Oracle NetSuite": [
      {
        id: "oracle-1",
        title: "Cloud Solutions Architect",
        location: "Austin, TX",
        type: "Full-time",
        salary: "$150,000 - $200,000",
        posted: "1 day ago",
        description: "Design enterprise cloud solutions for NetSuite customers.",
        requirements: ["NetSuite", "Cloud architecture", "7+ years experience"],
        benefits: ["Stock options", "Health insurance", "401k matching"]
      },
      {
        id: "oracle-2",
        title: "Senior Java Developer",
        location: "Redwood City, CA",
        type: "Full-time",
        salary: "$140,000 - $180,000",
        posted: "2 days ago",
        description: "Develop core NetSuite platform features.",
        requirements: ["Java", "Spring", "Oracle DB", "5+ years experience"],
        benefits: ["Remote work", "Health insurance", "Learning budget"]
      }
    ],
    "Microsoft Dynamics": [
      {
        id: "ms-1",
        title: "AI/ML Engineer",
        location: "Redmond, WA",
        type: "Full-time",
        salary: "$160,000 - $220,000",
        posted: "1 day ago",
        description: "Build AI features for Dynamics 365 platform.",
        requirements: ["Python", "TensorFlow", "Azure ML", "5+ years experience"],
        benefits: ["Stock options", "Health insurance", "401k matching"]
      },
      {
        id: "ms-2",
        title: "Senior Software Engineer",
        location: "Bellevue, WA",
        type: "Full-time",
        salary: "$140,000 - $190,000",
        posted: "3 days ago",
        description: "Develop Dynamics 365 Business Central features.",
        requirements: ["C#", ".NET", "Azure", "6+ years experience"],
        benefits: ["Remote work", "Health insurance", "Learning budget"]
      }
    ],
    "Workday": [
      {
        id: "workday-1",
        title: "Data Scientist",
        location: "Pleasanton, CA",
        type: "Full-time",
        salary: "$140,000 - $180,000",
        posted: "2 days ago",
        description: "Build predictive analytics for HR and finance software.",
        requirements: ["Python", "R", "Machine Learning", "4+ years experience"],
        benefits: ["Stock options", "Health insurance", "401k matching"]
      },
      {
        id: "workday-2",
        title: "Frontend Engineer",
        location: "San Francisco, CA",
        type: "Full-time",
        salary: "$130,000 - $170,000",
        posted: "1 week ago",
        description: "Build modern React applications for Workday platform.",
        requirements: ["React", "TypeScript", "4+ years experience"],
        benefits: ["Remote work", "Health insurance", "Learning budget"]
      }
    ],
    "Bill.com": [
      {
        id: "bill-1",
        title: "Frontend Developer",
        location: "San Jose, CA",
        type: "Full-time",
        salary: "$120,000 - $160,000",
        posted: "3 days ago",
        description: "Build user interfaces for payment processing platform.",
        requirements: ["React", "JavaScript", "3+ years experience"],
        benefits: ["Stock options", "Health insurance", "Flexible hours"]
      },
      {
        id: "bill-2",
        title: "Backend Engineer",
        location: "Palo Alto, CA",
        type: "Full-time",
        salary: "$130,000 - $170,000",
        posted: "1 week ago",
        description: "Develop APIs for financial transaction processing.",
        requirements: ["Java", "Spring", "AWS", "4+ years experience"],
        benefits: ["Remote work", "Health insurance", "Learning budget"]
      }
    ],
    "ADP": [
      {
        id: "adp-1",
        title: "DevOps Engineer",
        location: "Roseland, NJ",
        type: "Full-time",
        salary: "$120,000 - $160,000",
        posted: "2 days ago",
        description: "Manage cloud infrastructure for payroll and HR platform.",
        requirements: ["Docker", "Kubernetes", "AWS", "4+ years experience"],
        benefits: ["Health insurance", "401k matching", "Learning budget"]
      },
      {
        id: "adp-2",
        title: "Security Engineer",
        location: "New York, NY",
        type: "Full-time",
        salary: "$130,000 - $170,000",
        posted: "1 week ago",
        description: "Ensure security compliance for financial data processing.",
        requirements: ["Security", "Compliance", "5+ years experience"],
        benefits: ["Stock options", "Health insurance", "Conference budget"]
      }
    ]
  }

  const agentScreenings = [
    { company: "N/A", claim: "No AI claims detected yet", hypeScore: 0, realityScore: 0, status: "pending" },
  ]

  const handleTestScraping = async () => {
    setIsScrapingTest(true)
    try {
      // Use live scraping endpoint for enhanced scraping with 25 reviews
      const endpoint = "http://localhost:8000/api/scrape/live"
      const body = {
        companies: selectedCompanies.length > 0 ? selectedCompanies : ["Sage"] // Default to Sage if no companies selected
      }
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })

      // ───────────────────────────────────────────────────────────────
      // Always attempt to read JSON first; if that fails, fall back to
      // text and wrap it in a JSON-compatible structure so the UI
      // remains stable.
      // ───────────────────────────────────────────────────────────────
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

      // Transform backend data to match frontend expectations
      const transformedData = {
        success: data.success,
        summary: {
          totalReviews: data.totalReviews || 0,
          g2Reviews: data.platformBreakdown?.g2 || 0,
          glassdoorReviews: data.platformBreakdown?.glassdoor || 0,
          capterraReviews: data.platformBreakdown?.capterra || 0,
          companiesAnalyzed: data.companiesProcessed || 0,
          averageSentiment: data.averageSentiment || 0,
          avgProcessingTime: data.processingTime || "N/A"
        },
        platformBreakdown: {
          g2: {
            avgSentiment: (() => {
              const company = data.companyResults?.find((c: any) => c.platforms?.g2)
              const g2Data = company?.platforms?.g2
              return typeof g2Data === 'object' ? g2Data.avgSentiment : 0
            })()
          },
          glassdoor: {
            avgSentiment: (() => {
              const company = data.companyResults?.find((c: any) => c.platforms?.glassdoor)
              const glassdoorData = company?.platforms?.glassdoor
              return typeof glassdoorData === 'object' ? glassdoorData.avgSentiment : 0
            })()
          },
          capterra: {
            avgSentiment: (() => {
              const company = data.companyResults?.find((c: any) => c.platforms?.capterra)
              const capterraData = company?.platforms?.capterra
              return typeof capterraData === 'object' ? capterraData.avgSentiment : 0
            })()
          }
        },
        companySentiments: data.companyResults?.reduce((acc: any, company: any) => {
          // Transform platforms to simple numbers for frontend compatibility
          const transformedPlatforms: any = {}
          if (company.platforms) {
            Object.keys(company.platforms).forEach(platform => {
              const platformData = company.platforms[platform]
              if (typeof platformData === 'object' && platformData.reviews) {
                transformedPlatforms[platform] = platformData.reviews
              } else {
                transformedPlatforms[platform] = platformData || 0
              }
            })
          }
          
          acc[company.company.toLowerCase()] = {
            averageSentiment: company.averageSentiment,
            totalReviews: company.totalReviews,
            platforms: transformedPlatforms
          }
          return acc
        }, {}) || {},
        errors: data.errors || [],
        isLiveData: true
      }

      setScrapingResults(transformedData)

      if (data.success) {
        console.log("✅ LIVE scraping completed:", transformedData)
      } else {
        console.error("❌ LIVE scraping reported failure:", data)
      }
    } catch (err) {
      console.error("❌ Network or proxy error:", err)
      setScrapingResults({
        success: false,
        error: err instanceof Error ? err.message : "Unknown error",
      })
    } finally {
      setIsScrapingTest(false)
    }
  }

  const handleGetSentimentAnalysis = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/scrape/live-sentiment?action=recent")
      const data = await response.json()
      
      if (data.success && data.recentData) {
        console.log("✅ Sentiment analysis data loaded:", data.recentData)
        // Update company data with real sentiment analysis
        const updatedCompetitors = companyData.map(name => {
          const companyData = data.recentData.find((item: any) => 
            item.company.toLowerCase() === name.toLowerCase()
          )
          
          if (companyData) {
            return {
              name,
              sentiment: companyData.sentiment_score || "N/A",
              volume: companyData.sentiment_confidence || "N/A",
              realData: true,
              sources: {
                x: "N/A",
                reddit: "N/A",
                g2: companyData.platform === 'g2' ? 1 : 0,
                youtube: "N/A",
                glassdoor: companyData.platform === 'glassdoor' ? 1 : 0,
                capterra: companyData.platform === 'capterra' ? 1 : 0
              }
            }
          }
          return {
            name,
            sentiment: "N/A",
            volume: "N/A",
            realData: false,
            sources: {
              x: "N/A",
              reddit: "N/A",
              g2: "N/A",
              youtube: "N/A",
              glassdoor: "N/A",
              capterra: "N/A"
            }
          }
        })
        
        setCompetitorsData(updatedCompetitors)
      }
    } catch (err) {
      console.error("❌ Failed to fetch sentiment analysis:", err)
    }
  }

  // Initialize competitorsData with company data
  useEffect(() => {
    const initialCompetitors = companyData.map(name => ({
      name,
      sentiment: "N/A",
      volume: "N/A",
      realData: false,
      sources: {
        x: "N/A",
        reddit: "N/A",
        g2: "N/A",
        youtube: "N/A",
        glassdoor: "N/A",
        capterra: "N/A"
      }
    }))
    setCompetitorsData(initialCompetitors)
  }, [])

  // Load recent data when component mounts
  useEffect(() => {
    if (competitorsData.length > 0) {
      handleGetSentimentAnalysis()
    }
  }, [competitorsData.length])

  // --- DUMMY DATA INJECTION FOR SENTIMENT/REVIEWS ---
  // (REMOVED: revert to only show real/mock-scraped data)

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "critical":
        return <AlertTriangle className="h-4 w-4 text-red-600" />
      case "opportunity":
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case "intel":
        return <Users className="h-4 w-4 text-blue-600" />
      case "screening":
        return <Zap className="h-4 w-4 text-purple-600" />
      default:
        return <Activity className="h-4 w-4 text-gray-500" />
    }
  }

  const handleCompanySelect = (company: string) => {
    setSelectedCompanies((prev) => (prev.includes(company) ? prev.filter((c) => c !== company) : [...prev, company]))
  }

  const clearCompanySelection = () => {
    setSelectedCompanies([])
  }

  const handleSourceToggle = (source: string) => {
    setSelectedSources(prev => 
      prev.includes(source)
        ? prev.filter(s => s !== source)
        : [...prev, source]
    )
  }

  const handleSelectAllSources = () => {
    setSelectedSources(["g2", "glassdoor", "capterra", "reddit", "youtube", "x"])
  }

  const handleDeselectAllSources = () => {
    setSelectedSources([])
  }

  const handleJobDetailsClick = (company: string) => {
    setSelectedJobCompany(company)
    setShowJobDetails(true)
  }

  const closeJobDetails = () => {
    setShowJobDetails(false)
    setSelectedJobCompany(null)
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-black dark:bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-8 h-8 bg-green-500 rounded flex items-center justify-center">
                <span className="text-black font-bold text-sm">S</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white dark:text-foreground">Competitive Intelligence</h1>
                <p className="text-gray-300 dark:text-muted-foreground text-sm">Real-time market insights and competitor analysis</p>
              </div>
            </div>
            <div className="flex items-center gap-2 md:gap-3">
              <ThemeToggle />
              <Button
                onClick={handleTestScraping}
                disabled={isScrapingTest}
                variant="outline"
                size="sm"
                className="hidden md:flex border-green-500 text-green-400 hover:bg-green-500 hover:text-black dark:border-green-400 dark:text-green-300 dark:hover:bg-green-600 dark:hover:text-white bg-transparent"
              >
                {isScrapingTest ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Play className="h-4 w-4 mr-2" />}
                {isScrapingTest ? "Live Scraping..." : "Live Scrape"}
              </Button>
              <Button
                onClick={handleTestScraping}
                disabled={isScrapingTest}
                variant="outline"
                size="sm"
                className="md:hidden border-green-500 text-green-400 hover:bg-green-500 hover:text-black dark:border-green-400 dark:text-green-300 dark:hover:bg-green-600 dark:hover:text-white bg-transparent"
              >
                {isScrapingTest ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              </Button>
              <Link href="/captcha-solver">
                <Button
                  variant="outline"
                  size="sm"
                  className="hidden md:flex border-blue-500 text-blue-400 hover:bg-blue-500 hover:text-black dark:border-blue-400 dark:text-blue-300 dark:hover:bg-blue-600 dark:hover:text-white bg-transparent"
                >
                  🔐 CAPTCHA Solver
                </Button>
              </Link>
              <Link href="/captcha-solver">
                <Button
                  variant="outline"
                  size="sm"
                  className="md:hidden border-blue-500 text-blue-400 hover:bg-blue-500 hover:text-black dark:border-blue-400 dark:text-blue-300 dark:hover:bg-blue-600 dark:hover:text-white bg-transparent"
                >
                  🔐
                </Button>
              </Link>
              <Button
                variant="outline"
                size="sm"
                className="hidden md:flex border-gray-300 text-white hover:bg-gray-800 hover:text-white dark:border-gray-600 dark:text-foreground dark:hover:bg-accent bg-transparent"
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="md:hidden border-gray-300 text-white hover:bg-gray-800 hover:text-white dark:border-gray-600 dark:text-foreground dark:hover:bg-accent bg-transparent"
              >
                <Download className="h-4 w-4" />
              </Button>
              <Button size="sm" className="bg-green-500 hover:bg-green-600 text-white">
                <Bell className="h-4 w-4 mr-1 md:mr-2" />
                <span className="hidden md:inline">Alerts ({alerts.length})</span>
                <span className="md:hidden">{alerts.length}</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-6 py-4 md:py-6 space-y-4 md:space-y-6">
        {/* Scraping Results */}
        {scrapingResults && (
          <Card className="border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950/30">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-700 dark:text-green-400" />
                <CardTitle className="text-green-900 dark:text-green-100">Live Scraping Results</CardTitle>
                <Badge className="bg-green-600 text-white">{scrapingResults.summary?.totalReviews || 0} Reviews</Badge>
                {scrapingResults.isLiveData && <Badge className="bg-blue-600 text-white">LIVE DATA</Badge>}
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-3 bg-white dark:bg-gray-900/50 rounded-lg border border-green-200 dark:border-green-800/50">
                  <div className="text-sm text-green-700 dark:text-green-300">G2 Reviews</div>
                  <div className="text-2xl font-bold text-green-900 dark:text-green-100">{scrapingResults.summary?.g2Reviews || 0}</div>
                  <div className="text-xs text-green-600 dark:text-green-400">
                    Avg Sentiment: {Math.round((scrapingResults.platformBreakdown?.g2?.avgSentiment || 0) * 100)}%
                  </div>
                </div>
                <div className="p-3 bg-white dark:bg-gray-900/50 rounded-lg border border-green-200 dark:border-green-800/50">
                  <div className="text-sm text-green-700 dark:text-green-300">Glassdoor Reviews</div>
                  <div className="text-2xl font-bold text-green-900 dark:text-green-100">{scrapingResults.summary?.glassdoorReviews || 0}</div>
                  <div className="text-xs text-green-600 dark:text-green-400">
                    Avg Sentiment: {Math.round((scrapingResults.platformBreakdown?.glassdoor?.avgSentiment || 0) * 100)}%
                  </div>
                </div>
                <div className="p-3 bg-white dark:bg-gray-900/50 rounded-lg border border-green-200 dark:border-green-800/50">
                  <div className="text-sm text-green-700 dark:text-green-300">Capterra Reviews</div>
                  <div className="text-2xl font-bold text-green-900 dark:text-green-100">{scrapingResults.summary?.capterraReviews || 0}</div>
                  <div className="text-xs text-green-600 dark:text-green-400">
                    Avg Sentiment: {Math.round((scrapingResults.platformBreakdown?.capterra?.avgSentiment || 0) * 100)}%
                  </div>
                </div>
                <div className="p-3 bg-white dark:bg-gray-900/50 rounded-lg border border-green-200 dark:border-green-800/50">
                  <div className="text-sm text-green-700 dark:text-green-300">Companies Analyzed</div>
                  <div className="text-2xl font-bold text-green-900 dark:text-green-100">
                    {scrapingResults.summary?.companiesAnalyzed || 0}
                  </div>
                  <div className="text-xs text-green-600 dark:text-green-400">
                    Processing Time: {scrapingResults.summary?.avgProcessingTime || "N/A"}
                  </div>
                </div>
              </div>

              {/* Show errors if any */}
              {scrapingResults.errors && scrapingResults.errors.length > 0 && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="text-sm text-yellow-800 font-medium">Scraping Warnings:</div>
                  <ul className="text-xs text-yellow-700 mt-1">
                    {scrapingResults.errors.slice(0, 3).map((error: string, index: number) => (
                      <li key={index}>• {error}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Quick Filters */}
        <Card className="border-green-200 dark:border-green-800">
          <CardContent className="pt-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-green-600 dark:text-green-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filters</span>
              </div>

              {/* Multi-select Company Filter */}
              <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    className="w-60 justify-between border-gray-300 dark:border-gray-600 focus:border-green-500 bg-transparent dark:bg-gray-800"
                  >
                    {selectedCompanies.length === 0
                      ? "All Companies"
                      : selectedCompanies.length === 1
                        ? selectedCompanies[0]
                        : `${selectedCompanies.length} companies selected`}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-60 p-0">
                  <Command>
                    <CommandInput placeholder="Search companies..." />
                    <CommandList>
                      <CommandEmpty>No companies found.</CommandEmpty>
                      <CommandGroup>
                        {companyData.map((company) => (
                          <CommandItem key={company} value={company} onSelect={() => handleCompanySelect(company)}>
                            <Check
                              className={cn(
                                "mr-2 h-4 w-4",
                                selectedCompanies.includes(company) ? "opacity-100" : "opacity-0",
                              )}
                            />
                            {company}
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>

              {selectedCompanies.length > 0 && (
                <Button onClick={clearCompanySelection} variant="outline" size="sm">
                  Clear Selection ({selectedCompanies.length})
                </Button>
              )}

              <div className="flex items-center gap-2">
                <Button
                  onClick={handleSelectAllSources}
                  variant="outline"
                  size="sm"
                  className="border-green-500 text-green-400 hover:bg-green-500 hover:text-black dark:border-green-400 dark:text-green-300 dark:hover:bg-green-600 dark:hover:text-white bg-transparent"
                >
                  Select All
                </Button>
                <Button
                  onClick={handleDeselectAllSources}
                  variant="outline"
                  size="sm"
                  className="border-red-500 text-red-400 hover:bg-red-500 hover:text-black dark:border-red-400 dark:text-red-300 dark:hover:bg-red-600 dark:hover:text-white bg-transparent"
                >
                  Deselect All
                </Button>
              </div>

              {/* Multi-select Source Filter */}
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    role="combobox"
                    className="w-48 justify-between border-gray-300 focus:border-green-500 bg-transparent"
                  >
                    {selectedSources.length === 0
                      ? "Select Sources"
                      : selectedSources.length === 1
                        ? selectedSources[0].toUpperCase()
                        : `${selectedSources.length} sources selected`}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-48 p-0">
                  <Command>
                    <CommandInput placeholder="Search sources..." />
                    <CommandList>
                      <CommandEmpty>No sources found.</CommandEmpty>
                      <CommandGroup>
                        {[
                          { value: "g2", label: "G2 Reviews" },
                          { value: "glassdoor", label: "Glassdoor" },
                          { value: "capterra", label: "Capterra" },
                          { value: "reddit", label: "Reddit" },
                          { value: "youtube", label: "YouTube" },
                          { value: "x", label: "𝕏 (Twitter)" }
                        ].map((source) => (
                          <CommandItem 
                            key={source.value} 
                            value={source.value} 
                            onSelect={() => handleSourceToggle(source.value)}
                          >
                            <Check
                              className={cn(
                                "mr-2 h-4 w-4",
                                selectedSources.includes(source.value) ? "opacity-100" : "opacity-0",
                              )}
                            />
                            {source.label}
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>

              <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger className="w-32 border-gray-300 focus:border-green-500">
                  <SelectValue placeholder="Time Range" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="24h">24 Hours</SelectItem>
                  <SelectItem value="7d">7 Days</SelectItem>
                  <SelectItem value="30d">30 Days</SelectItem>
                  <SelectItem value="90d">90 Days</SelectItem>
                </SelectContent>
              </Select>

              <div className="flex items-center gap-2 ml-auto">
                <Search className="h-4 w-4 text-gray-400" />
                <Input placeholder="Search mentions..." className="w-64 border-gray-300 focus:border-green-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Critical Alerts */}
        <Card
          className={`border-l-4 ${scrapingResults ? "border-l-green-400 bg-green-50 dark:border-l-green-500 dark:bg-green-950/20" : "border-l-gray-400 bg-gray-50 dark:border-l-gray-500 dark:bg-gray-950/20"}`}
        >
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className={`h-5 w-5 ${scrapingResults ? "text-green-600 dark:text-green-400" : "text-gray-600 dark:text-gray-400"}`} />
              <CardTitle className={scrapingResults ? "text-green-800 dark:text-green-100" : "text-gray-800 dark:text-gray-100"}>System Status</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {alerts.map((alert, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-white dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700"
                >
                  <div className="flex items-center gap-3">
                    {getAlertIcon(alert.type)}
                    <span className="text-sm font-medium dark:text-gray-100">{alert.message}</span>
                    <Badge variant="outline" className="text-xs">
                      {alert.source}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                      {alert.priority}
                    </Badge>
                    <span className="text-xs text-gray-500 dark:text-gray-400">{alert.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Main Tabs */}
        <Tabs defaultValue="sentiment" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-gray-100 dark:bg-gray-800">
            <TabsTrigger value="sentiment" className="data-[state=active]:bg-green-500 data-[state=active]:text-black dark:data-[state=active]:bg-green-600 dark:data-[state=active]:text-white">
              <MessageSquare className="h-4 w-4 mr-2" />
              Sentiment
            </TabsTrigger>
            <TabsTrigger value="hiring" className="data-[state=active]:bg-green-500 data-[state=active]:text-black dark:data-[state=active]:bg-green-600 dark:data-[state=active]:text-white">
              <Users className="h-4 w-4 mr-2" />
              Hiring Intel
            </TabsTrigger>
            <TabsTrigger
              value="agent-screening"
              className="data-[state=active]:bg-green-500 data-[state=active]:text-black dark:data-[state=active]:bg-green-600 dark:data-[state=active]:text-white"
            >
              <Zap className="h-4 w-4 mr-2" />
              AI Screening
            </TabsTrigger>
            <TabsTrigger value="digest" className="data-[state=active]:bg-green-500 data-[state=active]:text-black dark:data-[state=active]:bg-green-600 dark:data-[state=active]:text-white">
              <BarChart3 className="h-4 w-4 mr-2" />
              Weekly Digest
            </TabsTrigger>
          </TabsList>

          {/* Sentiment Analysis */}
          <TabsContent value="sentiment" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {filteredCompetitors.map((competitor, index) => (
                <Card key={index} className={competitor.isUs ? "border-green-500 bg-green-50 dark:border-green-400 dark:bg-green-950/20" : "border-gray-200 dark:border-gray-700"}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className={`text-lg ${competitor.isUs ? "text-green-800 dark:text-green-100" : "text-gray-900 dark:text-gray-100"}`}>
                        {competitor.name}
                        {competitor.isUs && <span className="text-xs ml-2 text-green-600 dark:text-green-400">(Us)</span>}
                        {competitor.realData && <Badge className="ml-2 text-xs bg-blue-500">LIVE</Badge>}
                      </CardTitle>
                      <div className="flex items-center gap-1">
                        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">{competitor.change}</span>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-600 dark:text-gray-300">Sentiment Score</span>
                          <Popover>
                            <PopoverTrigger asChild>
                              <span className="text-2xl font-bold text-gray-900 dark:text-gray-100 cursor-pointer hover:underline">
                                {typeof competitor.sentiment === "number"
                                  ? (competitor.sentiment > 0 ? "+" : "") + (competitor.sentiment * 100).toFixed(1) + "%"
                                  : competitor.sentiment}
                              </span>
                            </PopoverTrigger>
                            <PopoverContent className="w-80">
                              <div className="mb-2">
                                <div className="font-semibold text-gray-800 dark:text-gray-100 mb-1">Sentiment Score Insights</div>
                                <div className="text-sm text-gray-600 dark:text-gray-300">
                                  This score is calculated from user reviews and ratings across multiple platforms. Higher is more positive.
                                </div>
                              </div>
                              <div className="mb-2">
                                <div className="font-medium text-gray-700 dark:text-gray-200 mb-1">Source Breakdown</div>
                                <div className="grid grid-cols-2 gap-1 text-xs">
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">G2:</span>
                                    <span>{competitor.sources.g2}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">Glassdoor:</span>
                                    <span>{competitor.sources.glassdoor}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">Capterra:</span>
                                    <span>{competitor.sources.capterra}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">𝕏:</span>
                                    <span>{competitor.sources.x}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">Reddit:</span>
                                    <span>{competitor.sources.reddit}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">YouTube:</span>
                                    <span>{competitor.sources.youtube}</span>
                                  </div>
                                </div>
                              </div>
                              <div className="text-xs text-gray-500 dark:text-gray-400">
                                <b>Tip:</b> More reviews from more sources = more accurate sentiment!
                              </div>
                            </PopoverContent>
                          </Popover>
                        </div>
                        {typeof competitor.sentiment === "number" ? (
                          <Progress
                            value={((competitor.sentiment + 1) / 2) * 100}
                            className={`h-2 ${competitor.isUs ? "[&>div]:bg-green-500" : "[&>div]:bg-gray-400"}`}
                          />
                        ) : (
                          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                            <div className="h-2 bg-gray-300 rounded-full w-0"></div>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Total Mentions</span>
                        <span className="font-medium">{competitor.volume}</span>
                      </div>
                      {selectedSources.length > 0 && (
                        <div className="pt-2 border-t border-gray-100">
                          <div className="text-xs text-gray-500 mb-2">Source Breakdown:</div>
                          <div className="grid grid-cols-2 gap-1 text-xs">
                            <div className="flex justify-between">
                              <span className="text-gray-600">𝕏:</span>
                              <span>{competitor.sources.x}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Reddit:</span>
                              <span>{competitor.sources.reddit}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">G2:</span>
                              <span className={competitor.sources.g2 !== "N/A" ? "text-green-600 font-medium" : ""}>
                                {competitor.sources.g2}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Glassdoor:</span>
                              <span
                                className={competitor.sources.glassdoor !== "N/A" ? "text-green-600 font-medium" : ""}
                              >
                                {competitor.sources.glassdoor}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Capterra:</span>
                              <span
                                className={competitor.sources.capterra !== "N/A" ? "text-indigo-600 font-medium" : ""}
                              >
                                {competitor.sources.capterra || "N/A"}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Sentiment Trends</CardTitle>
                <CardDescription>
                  {scrapingResults
                    ? "Live sentiment comparison across platforms"
                    : "Start scraping to see sentiment comparison across platforms"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border-2 border-dashed border-gray-200">
                  <div className="text-center text-gray-600">
                    <BarChart3 className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                    <p className="font-medium">{scrapingResults ? "Chart Coming Soon" : "No Data Available"}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      {scrapingResults
                        ? "Visualization of live scraped data"
                        : 'Click "Live Scrape" to generate sentiment data'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Hiring Intelligence */}
          <TabsContent value="hiring" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Briefcase className="h-5 w-5 text-green-600" />
                    Recent Hiring Activity
                  </CardTitle>
                  <CardDescription>Live hiring activity from top competitors</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {hiringTrends.map((trend, index) => (
                      <div 
                        key={index} 
                        className="flex items-center justify-between p-4 border rounded-lg bg-gray-50 dark:bg-gray-800 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        onClick={() => handleJobDetailsClick(trend.company)}
                      >
                        <div className="flex-1">
                          <div className="font-medium text-gray-500 dark:text-gray-300">{trend.company}</div>
                          <div className="text-sm text-gray-400 dark:text-gray-400">{trend.role}</div>
                          <div className="text-xs text-gray-400 dark:text-gray-500">{trend.location}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-lg text-gray-500 dark:text-gray-300">{trend.count}</div>
                          <div className="text-sm text-gray-400 dark:text-gray-400">{trend.change}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Hiring Insights</CardTitle>
                  <CardDescription>Competitor hiring trends and analysis</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="h-4 w-4 text-green-600" />
                        <span className="font-medium text-green-700">High Growth Areas</span>
                      </div>
                      <p className="text-sm text-green-600">AI/ML roles up 45% across competitors</p>
                    </div>
                    
                    <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="flex items-center gap-2 mb-2">
                        <Target className="h-4 w-4 text-blue-600" />
                        <span className="font-medium text-blue-700">Hot Skills</span>
                      </div>
                      <p className="text-sm text-blue-600">Cloud, React, Python in high demand</p>
                    </div>
                    
                    <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="h-4 w-4 text-orange-600" />
                        <span className="font-medium text-orange-700">Market Alert</span>
                      </div>
                      <p className="text-sm text-orange-600">Microsoft Dynamics aggressively hiring</p>
                    </div>
                    
                    <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                      <div className="flex items-center gap-2 mb-2">
                        <BarChart3 className="h-4 w-4 text-purple-600" />
                        <span className="font-medium text-purple-700">Salary Trends</span>
                      </div>
                      <p className="text-sm text-purple-600">Senior roles: $120k-180k average</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Job Details Modal */}
          {showJobDetails && selectedJobCompany && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        {selectedJobCompany} Job Listings
                      </h2>
                      <p className="text-gray-600 dark:text-gray-400">
                        {detailedJobListings[selectedJobCompany as keyof typeof detailedJobListings]?.length || 0} open positions
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={closeJobDetails}
                      className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                    >
                      <XCircle className="h-4 w-4" />
                    </Button>
                  </div>
                  
                  <div className="space-y-4">
                    {detailedJobListings[selectedJobCompany as keyof typeof detailedJobListings]?.map((job) => (
                      <div key={job.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 bg-gray-50 dark:bg-gray-900">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
                              {job.title}
                            </h3>
                            <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                              <span className="flex items-center gap-1">
                                <Briefcase className="h-4 w-4" />
                                {job.location}
                              </span>
                              <span className="flex items-center gap-1">
                                <Users className="h-4 w-4" />
                                {job.type}
                              </span>
                              <span className="flex items-center gap-1">
                                <BarChart3 className="h-4 w-4" />
                                {job.salary}
                              </span>
                              <span className="text-xs text-gray-500 dark:text-gray-500">
                                Posted {job.posted}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="space-y-4">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Description</h4>
                            <p className="text-gray-600 dark:text-gray-400 text-sm">{job.description}</p>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Requirements</h4>
                              <div className="flex flex-wrap gap-2">
                                {job.requirements.map((req, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {req}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                            
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Benefits</h4>
                              <div className="flex flex-wrap gap-2">
                                {job.benefits.map((benefit, index) => (
                                  <Badge key={index} variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200 dark:bg-green-950/20 dark:text-green-400 dark:border-green-800">
                                    {benefit}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* AI Screening */}
          <TabsContent value="agent-screening" className="space-y-6">
            <AIScreeningChat 
              scrapedData={scrapingResults} 
              selectedCompany={selectedCompanies.length > 0 ? selectedCompanies[0] : undefined}
            />
          </TabsContent>

          {/* Weekly Digest */}
          <TabsContent value="digest" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="border-gray-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-gray-700">
                    <Target className="h-5 w-5" />
                    Key Insights
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="font-medium text-gray-500">
                      {scrapingResults ? "Live Data Insights" : "No Insights Available"}
                    </div>
                    <div className="text-sm text-gray-400">
                      {scrapingResults && scrapingResults.summary
                        ? `${scrapingResults.summary.totalReviews || 0} reviews analyzed from ${scrapingResults.summary.companiesAnalyzed || 0} companies`
                        : "Start scraping to generate insights"}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="h-5 w-5 text-gray-600" />
                    Monitoring
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Critical alerts</span>
                    <Badge variant="secondary">{scrapingResults ? "Active" : "N/A"}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">AI announcements</span>
                    <Badge variant="secondary">N/A</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Hiring spikes</span>
                    <Badge variant="secondary">N/A</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Live data status</span>
                    <Badge variant="secondary">{scrapingResults ? "Connected" : "Disconnected"}</Badge>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-gray-600" />
                    Action Items
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="p-3 border rounded-lg bg-gray-50 border-gray-200">
                    <div className="font-medium text-sm text-gray-500">
                      {scrapingResults ? "Review Live Data" : "No Action Items"}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {scrapingResults
                        ? "Analyze scraped sentiment data for competitive insights"
                        : "Generate reports to see action items"}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Executive Summary</CardTitle>
                <CardDescription>Auto-generated weekly intelligence report</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="p-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border-2 border-dashed border-gray-200">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-gray-400 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Download className="h-8 w-8 text-white" />
                    </div>
                    <div className="mb-4">
                      <div className="text-xl font-bold text-gray-700">Weekly Intelligence Report</div>
                      <div className="text-sm text-gray-500">
                        {scrapingResults ? "Live data available" : "No data available"}
                      </div>
                    </div>
                    <p className="text-sm text-gray-500 mb-4">
                      {scrapingResults
                        ? "Live scraped data ready for comprehensive analysis including sentiment trends and competitive insights"
                        : "Start scraping to generate comprehensive analysis including sentiment trends, competitive moves, and market intelligence"}
                    </p>
                    <Button
                      disabled={!scrapingResults}
                      className={
                        scrapingResults
                          ? "bg-green-500 hover:bg-green-600 text-white"
                          : "bg-gray-300 text-gray-500 cursor-not-allowed"
                      }
                    >
                      <Download className="h-4 w-4 mr-2" />
                      {scrapingResults ? "Generate Report" : "No Report Available"}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Chat Widget */}
      <ChatWidget scrapedData={scrapingResults} />
    </div>
  )
}
