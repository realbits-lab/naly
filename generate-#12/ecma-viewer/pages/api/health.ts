import type { NextApiRequest, NextApiResponse } from 'next';
import { db } from '../../src/lib/db';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Simple connection test
    const stats = await db.getStatistics();
    res.status(200).json({ 
      status: 'healthy', 
      database: 'connected', 
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Health check failed:', error);
    res.status(500).json({
      status: 'error', 
      database: 'disconnected', 
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}