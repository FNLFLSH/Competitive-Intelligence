// Test script for AI Screening with dummy data
const fetch = require('node-fetch');

async function testAIScreening() {
  console.log('🧪 Testing AI Screening with dummy data...\n');

  try {
    // Test 1: Basic sentiment question
    console.log('📝 Test 1: Asking about Sage sentiment...');
    const response1 = await fetch('http://localhost:3000/api/chat/ai-screening', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: "What's the sentiment for Sage?",
        scrapedData: {},
        selectedCompany: "Sage",
        companyData: []
      }),
    });

    const data1 = await response1.json();
    console.log('✅ Response:', data1.response.substring(0, 100) + '...');
    console.log('📊 Metadata:', data1.metadata);
    console.log('');

    // Test 2: Rating question
    console.log('📝 Test 2: Asking about QuickBooks rating...');
    const response2 = await fetch('http://localhost:3000/api/chat/ai-screening', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: "What's the average rating for QuickBooks?",
        scrapedData: {},
        selectedCompany: "QuickBooks",
        companyData: []
      }),
    });

    const data2 = await response2.json();
    console.log('✅ Response:', data2.response.substring(0, 100) + '...');
    console.log('📊 Metadata:', data2.metadata);
    console.log('');

    // Test 3: Comparison question
    console.log('📝 Test 3: Asking for company comparison...');
    const response3 = await fetch('http://localhost:3000/api/chat/ai-screening', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: "Compare the companies in the dataset",
        scrapedData: {},
        selectedCompany: "",
        companyData: []
      }),
    });

    const data3 = await response3.json();
    console.log('✅ Response:', data3.response.substring(0, 100) + '...');
    console.log('📊 Metadata:', data3.metadata);
    console.log('');

    console.log('🎉 All tests completed!');

  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

testAIScreening(); 