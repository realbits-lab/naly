import { NextRequest, NextResponse } from 'next/server'

export async function GET() {
  const envVars = {
    GOOGLE_API_KEY: process.env.GOOGLE_API_KEY ? 'Set' : 'Not set',
    NODE_ENV: process.env.NODE_ENV,
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL ? 'Set' : 'Not set'
  }
  
  return NextResponse.json({ 
    message: 'Environment check',
    envVars
  })
} 