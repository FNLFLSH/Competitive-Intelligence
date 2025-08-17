"use client";

import { useState, useEffect, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, CheckCircle, AlertCircle, Play } from "lucide-react";

interface CaptchaData {
  captcha_id: string;
  company_name: string;
  platform: string;
  url: string;
  captcha_image: string;
}

interface LogMessage {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error';
}

export default function CaptchaSolverPage() {
  const [status, setStatus] = useState<string>("Waiting for CAPTCHA...");
  const [statusType, setStatusType] = useState<'info' | 'success' | 'error'>('info');
  const [captchaData, setCaptchaData] = useState<CaptchaData | null>(null);
  const [captchaSolution, setCaptchaSolution] = useState<string>("");
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isScraping, setIsScraping] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8001/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setStatus("Connected to server");
      setStatusType('success');
      addLog('WebSocket connected', 'success');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    ws.onclose = () => {
      setIsConnected(false);
      setStatus("Disconnected from server");
      setStatusType('error');
      addLog('WebSocket disconnected', 'error');
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };
  };

  const handleWebSocketMessage = (data: any) => {
    if (data.type === 'captcha_request') {
      setCaptchaData(data);
      setStatus("CAPTCHA detected! Please solve it.");
      setStatusType('info');
      addLog(`CAPTCHA detected for ${data.company_name} on ${data.platform}`, 'info');
    } else if (data.type === 'scraping_status') {
      addLog(data.message, 'info');
    } else if (data.type === 'scraping_complete') {
      setStatus("Scraping completed!");
      setStatusType('success');
      setIsScraping(false);
      addLog(`Scraping completed with ${data.review_count} reviews`, 'success');
    }
  };

  const addLog = (message: string, type: 'info' | 'success' | 'error') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }]);
  };

  const submitSolution = () => {
    if (!captchaSolution.trim()) {
      alert('Please enter a solution');
      return;
    }

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN && captchaData) {
      wsRef.current.send(JSON.stringify({
        type: 'captcha_solution',
        solution: captchaSolution,
        captcha_id: captchaData.captcha_id
      }));

      setCaptchaData(null);
      setCaptchaSolution("");
      setStatus("CAPTCHA solution submitted, continuing...");
      setStatusType('success');
      addLog(`CAPTCHA solution submitted: ${captchaSolution}`, 'success');
    }
  };

  const startScraping = (platform: 'g2' | 'glassdoor') => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'start_scraping',
        platform: platform,
        company_name: 'Sage'
      }));
      setStatus(`Starting ${platform} scraping...`);
      setStatusType('info');
      setIsScraping(true);
      addLog(`Starting ${platform} scraping for Sage`, 'info');
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">🔐 CAPTCHA Solver Interface</h1>
        <p className="text-muted-foreground">
          Solve CAPTCHAs manually and continue scraping automatically
        </p>
      </div>

      {/* Status Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {statusType === 'success' && <CheckCircle className="h-5 w-5 text-green-500" />}
            {statusType === 'error' && <AlertCircle className="h-5 w-5 text-red-500" />}
            {statusType === 'info' && <Loader2 className="h-5 w-5 text-blue-500" />}
            Current Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert className={statusType === 'success' ? 'border-green-200 bg-green-50' : 
                          statusType === 'error' ? 'border-red-200 bg-red-50' : 
                          'border-blue-200 bg-blue-50'}>
            <AlertDescription>{status}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* CAPTCHA Solver Card */}
      {captchaData && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Solve CAPTCHA</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium">Company</label>
                <p className="text-sm text-muted-foreground">{captchaData.company_name}</p>
              </div>
              <div>
                <label className="text-sm font-medium">Platform</label>
                <Badge variant="outline">{captchaData.platform}</Badge>
              </div>
              <div>
                <label className="text-sm font-medium">URL</label>
                <p className="text-sm text-muted-foreground truncate">{captchaData.url}</p>
              </div>
            </div>
            
            <div>
              <label className="text-sm font-medium">CAPTCHA Image</label>
              <div className="mt-2 border rounded-lg p-4 bg-gray-50">
                <img 
                  src={`data:image/png;base64,${captchaData.captcha_image}`}
                  alt="CAPTCHA"
                  className="max-w-full h-auto"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Input
                placeholder="Enter CAPTCHA solution..."
                value={captchaSolution}
                onChange={(e) => setCaptchaSolution(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && submitSolution()}
              />
              <Button onClick={submitSolution} disabled={!captchaSolution.trim()}>
                Submit Solution
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Scraping Controls */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Start Scraping</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Button 
              onClick={() => startScraping('g2')} 
              disabled={!isConnected || isScraping}
              className="flex items-center gap-2"
            >
              <Play className="h-4 w-4" />
              Start G2 Scraping for Sage
            </Button>
            <Button 
              onClick={() => startScraping('glassdoor')} 
              disabled={!isConnected || isScraping}
              variant="outline"
              className="flex items-center gap-2"
            >
              <Play className="h-4 w-4" />
              Start Glassdoor Scraping for Sage
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Logs */}
      <Card>
        <CardHeader>
          <CardTitle>Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-50 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
            {logs.map((log, index) => (
              <div key={index} className="mb-1">
                <span className="text-gray-500">[{log.timestamp}]</span>{' '}
                <span className={
                  log.type === 'success' ? 'text-green-600' :
                  log.type === 'error' ? 'text-red-600' :
                  'text-gray-700'
                }>
                  {log.message}
                </span>
              </div>
            ))}
            {logs.length === 0 && (
              <div className="text-gray-500">No logs yet...</div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 