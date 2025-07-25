Write-Host "🧪 Testing AI Screening with dummy data..." -ForegroundColor Green
Write-Host ""

# Test 1: Basic sentiment question
Write-Host "📝 Test 1: Asking about Sage sentiment..." -ForegroundColor Yellow
$body1 = @{
    message = "What's the sentiment for Sage?"
    scrapedData = @{}
    selectedCompany = "Sage"
    companyData = @()
} | ConvertTo-Json

try {
    $response1 = Invoke-WebRequest -Uri "http://localhost:3000/api/chat/ai-screening" -Method POST -Body $body1 -ContentType "application/json"
    $data1 = $response1.Content | ConvertFrom-Json
    Write-Host "✅ Response: $($data1.response.Substring(0, [Math]::Min(100, $data1.response.Length)))..." -ForegroundColor Green
    Write-Host "📊 Metadata: $($data1.metadata | ConvertTo-Json -Compress)" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "❌ Test 1 failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Rating question
Write-Host "📝 Test 2: Asking about QuickBooks rating..." -ForegroundColor Yellow
$body2 = @{
    message = "What's the average rating for QuickBooks?"
    scrapedData = @{}
    selectedCompany = "QuickBooks"
    companyData = @()
} | ConvertTo-Json

try {
    $response2 = Invoke-WebRequest -Uri "http://localhost:3000/api/chat/ai-screening" -Method POST -Body $body2 -ContentType "application/json"
    $data2 = $response2.Content | ConvertFrom-Json
    Write-Host "✅ Response: $($data2.response.Substring(0, [Math]::Min(100, $data2.response.Length)))..." -ForegroundColor Green
    Write-Host "📊 Metadata: $($data2.metadata | ConvertTo-Json -Compress)" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "❌ Test 2 failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Comparison question
Write-Host "📝 Test 3: Asking for company comparison..." -ForegroundColor Yellow
$body3 = @{
    message = "Compare the companies in the dataset"
    scrapedData = @{}
    selectedCompany = ""
    companyData = @()
} | ConvertTo-Json

try {
    $response3 = Invoke-WebRequest -Uri "http://localhost:3000/api/chat/ai-screening" -Method POST -Body $body3 -ContentType "application/json"
    $data3 = $response3.Content | ConvertFrom-Json
    Write-Host "✅ Response: $($data3.response.Substring(0, [Math]::Min(100, $data3.response.Length)))..." -ForegroundColor Green
    Write-Host "📊 Metadata: $($data3.metadata | ConvertTo-Json -Compress)" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "❌ Test 3 failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🎉 All tests completed!" -ForegroundColor Green 