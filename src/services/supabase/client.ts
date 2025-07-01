import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Type definitions for database tables
export interface Template {
  id: string
  title: string
  description: string
  thumbnail_url: string
  is_premium: boolean
  owner_id: string | null
  category_id: string
  created_at: string
  updated_at: string
  download_count: number
}

export interface Category {
  id: string
  name: string
  slug: string
  created_at: string
}

export interface Tag {
  id: string
  name: string
  slug: string
  type: 'style' | 'color' | 'subject'
  created_at: string
}

export interface UserProfile {
  id: string
  email: string
  name: string | null
  avatar_url: string | null
  role: 'free' | 'premium' | 'admin'
  created_at: string
}

export interface Subscription {
  id: string
  user_id: string
  plan: string
  status: string
  stripe_subscription_id: string | null
  current_period_end: string
  created_at: string
}

export interface Download {
  id: string
  user_id: string
  template_id: string
  timestamp: string
}