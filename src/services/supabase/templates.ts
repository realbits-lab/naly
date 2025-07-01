import { supabase, Template } from './client'

export class TemplateService {
  // Get all templates with filtering
  static async getTemplates(filters?: {
    categories?: string[]
    styles?: string[]
    premiumOnly?: boolean
    limit?: number
    offset?: number
  }) {
    let query = supabase
      .from('templates')
      .select(`
        *,
        categories!inner(name, slug),
        template_tags!inner(
          tags!inner(name, slug, type)
        )
      `)

    // Apply filters
    if (filters?.categories?.length) {
      query = query.in('categories.slug', filters.categories)
    }

    if (filters?.premiumOnly) {
      query = query.eq('is_premium', true)
    }

    if (filters?.limit) {
      query = query.limit(filters.limit)
    }

    if (filters?.offset) {
      query = query.range(filters.offset, filters.offset + (filters.limit || 20) - 1)
    }

    const { data, error } = await query.order('created_at', { ascending: false })

    if (error) throw error
    return data
  }

  // Get single template by ID
  static async getTemplate(id: string) {
    const { data, error } = await supabase
      .from('templates')
      .select(`
        *,
        categories(name, slug),
        template_tags(
          tags(name, slug, type)
        ),
        files(file_type, file_url)
      `)
      .eq('id', id)
      .single()

    if (error) throw error
    return data
  }

  // Search templates
  static async searchTemplates(query: string, limit = 20) {
    const { data, error } = await supabase
      .from('templates')
      .select('*')
      .textSearch('fts', query)
      .limit(limit)

    if (error) throw error
    return data
  }

  // Get templates by category
  static async getTemplatesByCategory(categorySlug: string, limit = 20) {
    const { data, error } = await supabase
      .from('templates')
      .select(`
        *,
        categories!inner(name, slug)
      `)
      .eq('categories.slug', categorySlug)
      .limit(limit)
      .order('created_at', { ascending: false })

    if (error) throw error
    return data
  }

  // Increment download count
  static async incrementDownloadCount(templateId: string) {
    const { error } = await supabase.rpc('increment_download_count', {
      template_id: templateId
    })

    if (error) throw error
  }

  // Record download
  static async recordDownload(userId: string, templateId: string) {
    const { error } = await supabase
      .from('downloads')
      .insert({
        user_id: userId,
        template_id: templateId,
        timestamp: new Date().toISOString()
      })

    if (error) throw error
  }
}