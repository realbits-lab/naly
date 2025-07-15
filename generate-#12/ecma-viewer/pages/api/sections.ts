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
    const { limit, offset, depth, search } = req.query;
    
    const limitNum = parseInt(limit as string || '100');
    const offsetNum = parseInt(offset as string || '0');
    const depthNum = depth ? parseInt(depth as string) : null;
    const searchStr = search as string;

    let sections;

    if (searchStr) {
      sections = await db.searchSections(searchStr, limitNum, offsetNum);
    } else if (depthNum !== null) {
      sections = await db.getSectionsByDepth(depthNum, limitNum, offsetNum);
    } else {
      sections = await db.getSections(limitNum, offsetNum);
    }

    res.status(200).json({ 
      sections,
      count: sections.length 
    });
  } catch (error) {
    console.error('Error fetching sections:', error);
    res.status(500).json({ 
      error: 'Failed to fetch sections',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}