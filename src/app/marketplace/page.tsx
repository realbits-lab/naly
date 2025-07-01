import { Suspense } from 'react'
import { TemplateGrid } from '@/features/templates/components/template-grid'
import { FilterSidebar } from '@/features/templates/components/filter-sidebar'
import { TemplateService } from '@/services/supabase/templates'

export default async function MarketplacePage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined }
}) {
  // Parse search params for filters
  const categories = Array.isArray(searchParams.categories) 
    ? searchParams.categories 
    : searchParams.categories ? [searchParams.categories] : []
    
  const styles = Array.isArray(searchParams.styles)
    ? searchParams.styles
    : searchParams.styles ? [searchParams.styles] : []

  const premiumOnly = searchParams.premium === 'true'

  // Mock templates data for now - will be replaced with Supabase data
  const mockTemplates = [
    {
      id: '1',
      title: 'Modern Business Presentation',
      description: 'A sleek and professional template for business presentations',
      thumbnail_url: '/placeholder-template.jpg',
      is_premium: false,
      category: 'Business',
      download_count: 1234,
    },
    {
      id: '2',
      title: 'Creative Portfolio Template',
      description: 'Showcase your work with this creative portfolio design',
      thumbnail_url: '/placeholder-template.jpg',
      is_premium: true,
      category: 'Design',
      download_count: 567,
    },
  ]

  // Mock data for filter options
  const filterOptions = {
    categories: ['Business', 'Technology', 'Education', 'Marketing', 'Design'],
    styles: ['Modern', 'Minimalist', 'Creative', 'Professional', 'Colorful'],
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Template Marketplace</h1>
        <p className="text-muted-foreground">
          Discover and download professional templates for your projects
        </p>
      </div>

      <div className="flex gap-8">
        {/* Filter Sidebar */}
        <div className="w-64 shrink-0">
          <FilterSidebar
            categories={filterOptions.categories}
            styles={filterOptions.styles}
            onFilterChange={(filters) => {
              // This would update URL params in a client component
              console.log('Filters changed:', filters)
            }}
          />
        </div>

        {/* Templates Grid */}
        <div className="flex-1">
          <div className="mb-6">
            <p className="text-sm text-muted-foreground">
              Showing {mockTemplates.length} templates
            </p>
          </div>
          
          <Suspense fallback={<div>Loading templates...</div>}>
            <TemplateGrid templates={mockTemplates} />
          </Suspense>
        </div>
      </div>
    </div>
  )
}