const { Pool } = require('pg');

async function testDatabase() {
  const pool = new Pool({
    user: 'thomasjeon',
    host: 'localhost',
    database: 'ecma376_docs',
    port: 5432,
  });

  try {
    console.log('Testing database connection...');
    const client = await pool.connect();
    console.log('✅ Database connected successfully');
    
    const result = await client.query('SELECT COUNT(*) FROM ecma_sections');
    console.log(`✅ Found ${result.rows[0].count} sections in database`);
    
    client.release();
    await pool.end();
    
    console.log('✅ Database test completed successfully');
  } catch (error) {
    console.error('❌ Database test failed:', error.message);
    process.exit(1);
  }
}

testDatabase();