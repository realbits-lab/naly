"use client";

import { useState, useEffect } from 'react'
import { TemplateService } from '@/services/supabase/templates'

interface UseTemplatesOptions {
  categories?: string[]
  styles?: string[]
  premiumOnly?: boolean
  limit?: number
}

export function useTemplates(options: UseTemplatesOptions = {}) {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await TemplateService.getTemplates(options)
        setTemplates(data || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch templates')
      } finally {
        setLoading(false)
      }
    }

    fetchTemplates()
  }, [JSON.stringify(options)])

  return { templates, loading, error, refetch: () => fetchTemplates() }
}

export function useTemplate(id: string) {
  const [template, setTemplate] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return

    const fetchTemplate = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await TemplateService.getTemplate(id)
        setTemplate(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch template')
      } finally {
        setLoading(false)
      }
    }

    fetchTemplate()
  }, [id])

  return { template, loading, error }
}

export function useTemplateSearch(query: string) {
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      return
    }

    const searchTemplates = async () => {
      try {
        setLoading(true)
        setError(null)
        const data = await TemplateService.searchTemplates(query)
        setResults(data || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Search failed')
      } finally {
        setLoading(false)
      }
    }

    const timeoutId = setTimeout(searchTemplates, 300) // Debounce search

    return () => clearTimeout(timeoutId)
  }, [query])

  return { results, loading, error }
}