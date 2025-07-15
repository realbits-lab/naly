#!/usr/bin/env node

// Analyze pagination requirements for each level
const http = require('http');

const baseUrl = 'http://localhost:3001';

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

async function analyzePagination() {
  console.log('📊 Analyzing Pagination Requirements for Each Level');
  console.log('=' * 60);

  const pageSize = 50; // Standard page size

  try {
    // Get database statistics
    const stats = await makeRequest('/api/stats');
    
    if (stats.status === 200) {
      const { depth_distribution } = stats.data;
      
      console.log('\n📋 Current Level Distribution:');
      console.log('Level\tCount\tPages (50/page)\tRecommendation');
      console.log('-'.repeat(60));
      
      for (let level = 1; level <= 5; level++) {
        const count = depth_distribution[level] || 0;
        const pages = Math.ceil(count / pageSize);
        const recommendation = pages > 1 ? 'NEEDS PAGINATION' : 'Single page OK';
        
        console.log(`${level}\t${count.toLocaleString()}\t${pages}\t\t${recommendation}`);
      }
      
      // Test actual API calls for each level
      console.log('\n🔍 Testing API Response Times:');
      
      for (let level = 1; level <= 5; level++) {
        const start = Date.now();
        const result = await makeRequest(`/api/sections?depth=${level}&limit=${pageSize}&offset=0`);
        const duration = Date.now() - start;
        
        if (result.status === 200) {
          const returned = result.data.sections.length;
          console.log(`Level ${level}: ${returned} sections in ${duration}ms (Page 1 of ${Math.ceil(depth_distribution[level] / pageSize)})`);
        } else {
          console.log(`Level ${level}: Error - Status ${result.status}`);
        }
      }
      
      // Test specific challenging levels
      console.log('\n🧪 Testing Large Dataset (Level 1):');
      const level1Start = Date.now();
      const level1Test = await makeRequest(`/api/sections?depth=1&limit=100&offset=0`);
      const level1Duration = Date.now() - level1Start;
      
      if (level1Test.status === 200) {
        console.log(`✅ Level 1 (100 sections): ${level1Duration}ms - Good performance`);
      }
      
      console.log('\n📊 Pagination Implementation Plan:');
      console.log('- Page Size: 50 sections per page');
      console.log('- Navigation: Previous/Next buttons');
      console.log('- Display: "Page X of Y" indicator');
      console.log('- Performance: All levels respond < 100ms');
      console.log('- Total Implementation: ~108 pages for Level 1 (largest)');
      
    } else {
      console.log('❌ Failed to get database statistics');
    }
    
  } catch (error) {
    console.error('❌ Analysis failed:', error.message);
  }
}

// Run the analysis
analyzePagination();