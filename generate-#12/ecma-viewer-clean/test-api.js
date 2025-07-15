#!/usr/bin/env node

// Simple test script to verify API endpoints work
const http = require('http');

const baseUrl = 'http://localhost:3000';

function makeRequest(path) {
  return new Promise((resolve, reject) => {
    http.get(`${baseUrl}${path}`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({
            status: res.statusCode,
            data: JSON.parse(data)
          });
        } catch (e) {
          resolve({
            status: res.statusCode,
            data: data
          });
        }
      });
    }).on('error', reject);
  });
}

async function runTests() {
  console.log('🚀 Testing ECMA-376 Database Viewer API endpoints...\n');

  try {
    // Test health endpoint
    console.log('1. Testing health endpoint...');
    const health = await makeRequest('/api/health');
    console.log(`   Status: ${health.status}`);
    console.log(`   Response: ${JSON.stringify(health.data, null, 2)}\n`);

    // Test stats endpoint
    console.log('2. Testing stats endpoint...');
    const stats = await makeRequest('/api/stats');
    console.log(`   Status: ${stats.status}`);
    if (stats.status === 200) {
      console.log(`   Total sections: ${stats.data.general?.total_sections || 'N/A'}`);
      console.log(`   Depth levels: ${Object.keys(stats.data.depth_distribution || {}).length}`);
    } else {
      console.log(`   Error: ${JSON.stringify(stats.data, null, 2)}`);
    }
    console.log('');

    // Test sections endpoint
    console.log('3. Testing sections endpoint...');
    const sections = await makeRequest('/api/sections?limit=5');
    console.log(`   Status: ${sections.status}`);
    if (sections.status === 200) {
      console.log(`   Returned ${sections.data.sections?.length || 0} sections`);
      if (sections.data.sections?.length > 0) {
        const first = sections.data.sections[0];
        console.log(`   First section: ${first.full_section_number} - ${first.title}`);
      }
    } else {
      console.log(`   Error: ${JSON.stringify(sections.data, null, 2)}`);
    }
    console.log('');

    // Test search endpoint
    console.log('4. Testing search functionality...');
    const search = await makeRequest('/api/sections?search=chart&limit=3');
    console.log(`   Status: ${search.status}`);
    if (search.status === 200) {
      console.log(`   Found ${search.data.sections?.length || 0} sections matching "chart"`);
      search.data.sections?.forEach((section, i) => {
        console.log(`   ${i + 1}. ${section.full_section_number} - ${section.title}`);
      });
    } else {
      console.log(`   Error: ${JSON.stringify(search.data, null, 2)}`);
    }
    console.log('');

    // Test depth filter
    console.log('5. Testing depth filter...');
    const depth = await makeRequest('/api/sections?depth=1&limit=3');
    console.log(`   Status: ${depth.status}`);
    if (depth.status === 200) {
      console.log(`   Found ${depth.data.sections?.length || 0} level 1 sections`);
      depth.data.sections?.forEach((section, i) => {
        console.log(`   ${i + 1}. ${section.full_section_number} - ${section.title} (Level ${section.depth})`);
      });
    } else {
      console.log(`   Error: ${JSON.stringify(depth.data, null, 2)}`);
    }

    console.log('\n✅ API testing completed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.log('\nMake sure the development server is running with: npm run dev');
  }
}

runTests();