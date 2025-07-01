import { notFound } from 'next/navigation'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Download, Heart, Share2, Eye } from 'lucide-react'

interface TemplateDetailPageProps {
  params: {
    id: string
  }
}

// Mock template data - will be replaced with Supabase data
const mockTemplate = {
  id: '1',
  title: 'Modern Business Presentation',
  description: 'A comprehensive business presentation template featuring modern design elements, professional layouts, and customizable sections for all your business needs.',
  thumbnail_url: '/placeholder-template.jpg',
  is_premium: false,
  category: 'Business',
  download_count: 1234,
  created_at: '2024-01-15',
  tags: ['Modern', 'Professional', 'Business'],
  files: [
    { file_type: 'pptx', file_url: '/template.pptx' },
    { file_type: 'googleslides', file_url: '/template-google' },
    { file_type: 'canva', file_url: '/template-canva' }
  ],
  preview_images: [
    '/slide-1.jpg',
    '/slide-2.jpg',
    '/slide-3.jpg',
    '/slide-4.jpg'
  ]
}

export default async function TemplateDetailPage({ params }: TemplateDetailPageProps) {
  const { id } = params
  
  // In production, fetch template from Supabase
  // const template = await TemplateService.getTemplate(id)
  
  if (!mockTemplate) {
    notFound()
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* Template Header */}
          <div className="mb-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold mb-2">{mockTemplate.title}</h1>
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline">{mockTemplate.category}</Badge>
                  {mockTemplate.is_premium && (
                    <Badge variant="secondary">Premium</Badge>
                  )}
                </div>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Download className="w-4 h-4" />
                    {mockTemplate.download_count} downloads
                  </span>
                  <span>Updated {mockTemplate.created_at}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <Heart className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <Share2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
            
            <p className="text-muted-foreground leading-relaxed">
              {mockTemplate.description}
            </p>
          </div>

          {/* Preview Images */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Preview</h2>
            <div className="grid grid-cols-2 gap-4">
              {mockTemplate.preview_images.map((image, index) => (
                <div key={index} className="relative aspect-video rounded-lg overflow-hidden border">
                  <Image
                    src={image}
                    alt={`Slide ${index + 1}`}
                    fill
                    className="object-cover"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Tags */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {mockTemplate.tags.map((tag) => (
                <Badge key={tag} variant="outline">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card className="sticky top-4">
            <CardHeader>
              <CardTitle>Download Template</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Download Options */}
              <div className="space-y-2">
                <p className="text-sm font-medium">Available formats:</p>
                {mockTemplate.files.map((file) => (
                  <Button
                    key={file.file_type}
                    variant="outline"
                    className="w-full justify-between"
                  >
                    <span className="capitalize">{file.file_type}</span>
                    <Download className="w-4 h-4" />
                  </Button>
                ))}
              </div>

              {/* Premium CTA or Download */}
              {mockTemplate.is_premium ? (
                <div className="pt-4 border-t">
                  <Button className="w-full mb-2">
                    Upgrade to Premium
                  </Button>
                  <p className="text-xs text-muted-foreground text-center">
                    Access this template and thousands more with a premium subscription
                  </p>
                </div>
              ) : (
                <div className="pt-4 border-t">
                  <Button className="w-full mb-2">
                    <Download className="w-4 h-4 mr-2" />
                    Download Free
                  </Button>
                  <p className="text-xs text-muted-foreground text-center">
                    Free download • No attribution required
                  </p>
                </div>
              )}

              {/* Stats */}
              <div className="pt-4 border-t">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Views</span>
                  <span className="flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    5,432
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm mt-2">
                  <span className="text-muted-foreground">Downloads</span>
                  <span className="flex items-center gap-1">
                    <Download className="w-4 h-4" />
                    {mockTemplate.download_count}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}