"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Loader2, 
  Zap,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Star,
  MessageSquare
} from "lucide-react"

interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: Date
  metadata?: {
    company?: string
    sentiment?: number
    rating?: number
    source?: string
  }
}

interface CompanyData {
  name: string
  reviews: any[]
  averageSentiment: number
  averageRating: number
  totalReviews: number
}

interface AIScreeningChatProps {
  scrapedData?: any
  selectedCompany?: string
}

export function AIScreeningChat({ scrapedData, selectedCompany }: AIScreeningChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! 👋 I'm your AI assistant for competitive intelligence. I can help you analyze company data, chat about anything, or answer questions about the companies in our system. What would you like to know?",
      sender: "assistant",
      timestamp: new Date(),
    },
  ])
  const [inputValue, setInputValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedCompanyForChat, setSelectedCompanyForChat] = useState(selectedCompany || "")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const companyData = scrapedData?.companyResults || []

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Update selected company when prop changes
  useEffect(() => {
    if (selectedCompany && selectedCompany !== selectedCompanyForChat) {
      setSelectedCompanyForChat(selectedCompany)
      // Add a system message about the company change
                        const systemMessage: Message = {
                    id: Date.now().toString(),
                    content: `Perfect! 🎯 I'm now focused on **${selectedCompany}**. I can help you analyze their reviews, sentiment, ratings, and answer any questions you have about them. What would you like to explore?`,
                    sender: "assistant",
                    timestamp: new Date(),
                  }
      setMessages(prev => [...prev, systemMessage])
    }
  }, [selectedCompany, selectedCompanyForChat])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)

    try {
      const response = await fetch("/api/chat/ai-screening", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: inputValue,
          scrapedData: scrapedData,
          selectedCompany: selectedCompanyForChat,
          companyData: companyData,
        }),
      })

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response || "I'm having trouble processing that request right now.",
        sender: "assistant",
        timestamp: new Date(),
        metadata: data.metadata,
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error("Chat error:", error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I'm having trouble connecting right now. Please try again later.",
        sender: "assistant",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const getSuggestedQuestions = () => {
    if (!selectedCompanyForChat) {
      return [
        "Hello! How are you?",
        "What can you help me with?",
        "Tell me about yourself",
        "What's the general sentiment about Sage?",
      ]
    }

    return [
      `Hello! How are you?`,
      `What's the general sentiment about ${selectedCompanyForChat}?`,
      `What's the average rating for ${selectedCompanyForChat}?`,
      `What are the most common complaints about ${selectedCompanyForChat}?`,
    ]
  }

  const handleSuggestedQuestion = (question: string) => {
    setInputValue(question)
  }

  const getSentimentIcon = (sentiment: number) => {
    if (sentiment > 0.1) return <TrendingUp className="h-4 w-4 text-green-500" />
    if (sentiment < -0.1) return <AlertTriangle className="h-4 w-4 text-red-500" />
    return <CheckCircle className="h-4 w-4 text-yellow-500" />
  }

  const getRatingStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        <Star className="h-3 w-3 text-yellow-400 fill-current" />
        <span className="text-sm font-medium">{rating.toFixed(1)}</span>
      </div>
    )
  }

                return (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6">
                  {/* Chat Interface */}
                  <div className="lg:col-span-2">
                    <Card className="h-[500px] md:h-[600px] flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 bg-gradient-to-r from-green-500 to-green-600 dark:from-green-600 dark:to-green-700 text-white rounded-t-lg">
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <Zap className="h-5 w-5" />
              AI Screening Assistant
            </CardTitle>
            <Badge variant="secondary" className="bg-green-400 dark:bg-green-300 text-white dark:text-black">
              {companyData.length > 0 ? `${companyData.length} companies` : "No data"}
            </Badge>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-0">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex items-start gap-3 ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  {message.sender === "assistant" && (
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-green-600" />
                    </div>
                  )}

                  <div
                    className={`max-w-[80%] p-3 rounded-lg text-sm ${
                      message.sender === "user" 
                        ? "bg-green-500 text-white" 
                        : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    
                    {/* Show metadata if available */}
                    {message.metadata && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          {message.metadata.company && (
                            <Badge variant="outline" className="text-xs">
                              {message.metadata.company}
                            </Badge>
                          )}
                          {message.metadata.sentiment !== undefined && (
                            <div className="flex items-center gap-1">
                              {getSentimentIcon(message.metadata.sentiment)}
                              <span>{(message.metadata.sentiment * 100).toFixed(1)}%</span>
                            </div>
                          )}
                          {message.metadata.rating && getRatingStars(message.metadata.rating)}
                        </div>
                      </div>
                    )}
                  </div>

                  {message.sender === "user" && (
                    <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4 text-gray-600" />
                    </div>
                  )}
                </div>
              ))}

              {isLoading && (
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-green-600 dark:text-green-400" />
                  </div>
                  <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                    <div className="flex space-x-1">
                      <Loader2 className="h-4 w-4 animate-spin text-green-600 dark:text-green-400" />
                      <span className="text-sm text-gray-600 dark:text-gray-300">Analyzing...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Say hello, ask about companies, or chat about anything..."
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={isLoading || !inputValue.trim()}
                  size="sm"
                  className="bg-green-500 hover:bg-green-600"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sidebar */}
      <div className="space-y-4">
        {/* Company Selector */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Select Company</CardTitle>
          </CardHeader>
          <CardContent>
            <Select value={selectedCompanyForChat} onValueChange={setSelectedCompanyForChat}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a company" />
              </SelectTrigger>
              <SelectContent>
                {companyData.map((company: any) => (
                  <SelectItem key={company.company} value={company.company}>
                    {company.company}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        {/* Suggested Questions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Suggested Questions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {getSuggestedQuestions().map((question, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                className="w-full justify-start text-left h-auto p-2 text-xs"
                onClick={() => handleSuggestedQuestion(question)}
              >
                <MessageSquare className="h-3 w-3 mr-2 text-gray-400" />
                {question}
              </Button>
            ))}
          </CardContent>
        </Card>

        {/* Quick Stats */}
        {selectedCompanyForChat && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Quick Stats</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {companyData
                .filter((company: any) => company.company === selectedCompanyForChat)
                .map((company: any) => (
                  <div key={company.company} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Average Rating</span>
                      <div className="flex items-center gap-1">
                        {getRatingStars(company.averageRating)}
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Sentiment</span>
                      <div className="flex items-center gap-1">
                        {getSentimentIcon(company.averageSentiment)}
                        <span className="text-xs font-medium">
                          {(company.averageSentiment * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Total Reviews</span>
                      <span className="text-xs font-medium">{company.totalReviews}</span>
                    </div>
                  </div>
                ))}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
} 