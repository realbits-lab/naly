import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '100');
    const offset = parseInt(searchParams.get('offset') || '0');
    const depth = searchParams.get('depth');
    const search = searchParams.get('search');

    let sections;

    if (search) {
      sections = await db.searchSections(search, limit, offset);
    } else if (depth) {
      sections = await db.getSectionsByDepth(parseInt(depth), limit, offset);
    } else {
      sections = await db.getSections(limit, offset);
    }

    return NextResponse.json({ 
      sections,
      count: sections.length 
    });
  } catch (error) {
    console.error('Error fetching sections:', error);
    return NextResponse.json(
      { error: 'Failed to fetch sections' },
      { status: 500 }
    );
  }
}