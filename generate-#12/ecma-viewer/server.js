#!/usr/bin/env node
const express = require('express');
const path = require('path');
const { Pool } = require('pg');

const app = express();
const port = 3000;

// Database connection
let pool = null;

function getPool() {
  if (!pool) {
    pool = new Pool({
      user: 'thomasjeon',
      host: 'localhost',
      database: 'ecma376_docs',
      port: 5432,
      max: 10,
      idleTimeoutMillis: 30000,
    });
  }
  return pool;
}

// Middleware
app.use(express.json());
app.use(express.static('public'));

// API Routes
app.get('/api/health', async (req, res) => {
  try {
    const client = await getPool().connect();
    await client.query('SELECT 1');
    client.release();
    res.json({ 
      status: 'healthy', 
      database: 'connected', 
      timestamp: new Date().toISOString() 
    });
  } catch (error) {
    res.status(500).json({ 
      status: 'error', 
      database: 'disconnected', 
      error: error.message 
    });
  }
});

app.get('/api/stats', async (req, res) => {
  try {
    const client = await getPool().connect();
    
    // Get general statistics
    const statsResult = await client.query(`
      SELECT 
        COUNT(*) as total_sections,
        COUNT(DISTINCT level1) as level1_count,
        COUNT(DISTINCT level2) as level2_count,
        COUNT(DISTINCT level3) as level3_count,
        COUNT(DISTINCT level4) as level4_count,
        COUNT(DISTINCT level5) as level5_count,
        COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END) as sections_with_embeddings
      FROM ecma_sections
    `);
    
    // Get depth distribution
    const depthResult = await client.query(`
      SELECT depth, COUNT(*) as count
      FROM ecma_sections
      GROUP BY depth
      ORDER BY depth
    `);
    
    // Get type distribution
    const typeResult = await client.query(`
      SELECT section_type, COUNT(*) as count
      FROM ecma_sections
      WHERE section_type IS NOT NULL
      GROUP BY section_type
      ORDER BY count DESC
    `);
    
    client.release();
    
    const stats = statsResult.rows[0];
    const depthDistribution = {};
    const typeDistribution = {};
    
    depthResult.rows.forEach(row => {
      depthDistribution[row.depth] = parseInt(row.count);
    });
    
    typeResult.rows.forEach(row => {
      typeDistribution[row.section_type] = parseInt(row.count);
    });
    
    res.json({
      general: {
        total_sections: parseInt(stats.total_sections),
        sections_with_embeddings: parseInt(stats.sections_with_embeddings),
        level1_count: parseInt(stats.level1_count),
        level2_count: parseInt(stats.level2_count),
        level3_count: parseInt(stats.level3_count),
        level4_count: parseInt(stats.level4_count),
        level5_count: parseInt(stats.level5_count),
      },
      depth_distribution: depthDistribution,
      type_distribution: typeDistribution,
    });
  } catch (error) {
    console.error('Error fetching statistics:', error);
    res.status(500).json({ error: 'Failed to fetch statistics' });
  }
});

app.get('/api/sections', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit || '100');
    const offset = parseInt(req.query.offset || '0');
    const depth = req.query.depth;
    const search = req.query.search;

    const client = await getPool().connect();
    let query, params;

    if (search) {
      query = `
        SELECT id, level1, level2, level3, level4, level5, 
               full_section_number, title, description, 
               page_reference, section_type, depth, parent_id,
               created_at, updated_at
        FROM ecma_sections 
        WHERE title ILIKE $1 OR description ILIKE $1
        ORDER BY full_section_number 
        LIMIT $2 OFFSET $3
      `;
      params = [`%${search}%`, limit, offset];
    } else if (depth) {
      query = `
        SELECT id, level1, level2, level3, level4, level5, 
               full_section_number, title, description, 
               page_reference, section_type, depth, parent_id,
               created_at, updated_at
        FROM ecma_sections 
        WHERE depth = $1
        ORDER BY full_section_number 
        LIMIT $2 OFFSET $3
      `;
      params = [parseInt(depth), limit, offset];
    } else {
      query = `
        SELECT id, level1, level2, level3, level4, level5, 
               full_section_number, title, description, 
               page_reference, section_type, depth, parent_id,
               created_at, updated_at
        FROM ecma_sections 
        ORDER BY full_section_number 
        LIMIT $1 OFFSET $2
      `;
      params = [limit, offset];
    }

    const result = await client.query(query, params);
    client.release();

    res.json({ 
      sections: result.rows,
      count: result.rows.length 
    });
  } catch (error) {
    console.error('Error fetching sections:', error);
    res.status(500).json({ error: 'Failed to fetch sections' });
  }
});

// Serve the HTML file
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(port, () => {
  console.log(`🚀 ECMA-376 Database Viewer running at http://localhost:${port}`);
  console.log(`📊 Database: ecma376_docs`);
  console.log(`📁 Serving static files from: public/`);
  console.log(`🔧 API endpoints:`);
  console.log(`   - GET /api/health`);
  console.log(`   - GET /api/stats`);
  console.log(`   - GET /api/sections`);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('Received SIGTERM, shutting down gracefully...');
  if (pool) {
    pool.end();
  }
  process.exit(0);
});