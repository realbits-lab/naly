'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { EcmaSection } from '@/lib/db';

interface SectionsTableProps {
  initialSections?: EcmaSection[];
}

export default function SectionsTable({ initialSections = [] }: SectionsTableProps) {
  const [sections, setSections] = useState<EcmaSection[]>(initialSections);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepth, setSelectedDepth] = useState<number | null>(null);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const limit = 50;

  const fetchSections = useCallback(async (reset = false) => {
    if (loading) return;
    
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('limit', limit.toString());
      
      if (reset) {
        params.set('offset', '0');
        setOffset(0);
      } else {
        params.set('offset', offset.toString());
      }
      
      if (searchTerm) {
        params.set('search', searchTerm);
      }
      
      if (selectedDepth !== null) {
        params.set('depth', selectedDepth.toString());
      }

      const response = await fetch(`/api/sections?${params.toString()}`);
      if (!response.ok) throw new Error('Failed to fetch');
      
      const data = await response.json();
      
      if (reset) {
        setSections(data.sections);
      } else {
        setSections(prev => [...prev, ...data.sections]);
      }
      
      setHasMore(data.sections.length === limit);
      if (!reset) {
        setOffset(prev => prev + limit);
      }
    } catch (error) {
      console.error('Error fetching sections:', error);
    } finally {
      setLoading(false);
    }
  }, [loading, limit, offset, searchTerm, selectedDepth]);

  const handleSearch = () => {
    fetchSections(true);
  };

  const handleDepthFilter = (depth: number | null) => {
    setSelectedDepth(depth);
    setSearchTerm(''); // Clear search when filtering by depth
    fetchSections(true);
  };

  const loadMore = () => {
    fetchSections(false);
  };

  useEffect(() => {
    if (initialSections.length === 0) {
      fetchSections(true);
    }
  }, [initialSections.length, fetchSections]);

  const getBadgeColor = (depth: number) => {
    const colors = [
      'bg-red-100 text-red-800',
      'bg-blue-100 text-blue-800', 
      'bg-green-100 text-green-800',
      'bg-yellow-100 text-yellow-800',
      'bg-purple-100 text-purple-800'
    ];
    return colors[depth - 1] || 'bg-gray-100 text-gray-800';
  };

  const truncateText = (text: string | null, maxLength: number = 100) => {
    if (!text) return '-';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  return (
    <div className="space-y-4">
      {/* Search and Filter Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div className="flex gap-2 flex-1">
          <Input
            placeholder="Search sections by title or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="flex-1"
          />
          <Button onClick={handleSearch} disabled={loading}>
            Search
          </Button>
        </div>
        
        <div className="flex gap-2 flex-wrap">
          <Button
            variant={selectedDepth === null ? "default" : "outline"}
            size="sm"
            onClick={() => handleDepthFilter(null)}
          >
            All Levels
          </Button>
          {[1, 2, 3, 4, 5].map(depth => (
            <Button
              key={depth}
              variant={selectedDepth === depth ? "default" : "outline"}
              size="sm"
              onClick={() => handleDepthFilter(depth)}
            >
              Level {depth}
            </Button>
          ))}
        </div>
      </div>

      {/* Results Info */}
      <div className="text-sm text-gray-600">
        Showing {sections.length} sections
        {selectedDepth && ` (Level ${selectedDepth} only)`}
        {searchTerm && ` matching "${searchTerm}"`}
      </div>

      {/* Table */}
      <div className="border rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[120px]">Section #</TableHead>
              <TableHead className="w-[80px]">Level</TableHead>
              <TableHead className="min-w-[200px]">Title</TableHead>
              <TableHead className="min-w-[300px]">Description</TableHead>
              <TableHead className="w-[100px]">Type</TableHead>
              <TableHead className="w-[100px]">Page Ref</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sections.map((section) => (
              <TableRow key={section.id} className="hover:bg-gray-50">
                <TableCell className="font-mono text-sm">
                  {section.full_section_number}
                </TableCell>
                <TableCell>
                  <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getBadgeColor(section.depth)}`}>
                    {section.depth}
                  </span>
                </TableCell>
                <TableCell className="font-medium">
                  {truncateText(section.title, 80)}
                </TableCell>
                <TableCell className="text-sm text-gray-600">
                  {truncateText(section.description, 150)}
                </TableCell>
                <TableCell className="text-sm">
                  {section.section_type || '-'}
                </TableCell>
                <TableCell className="text-sm">
                  {section.page_reference || '-'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Load More */}
      {hasMore && !searchTerm && !selectedDepth && (
        <div className="flex justify-center">
          <Button 
            onClick={loadMore} 
            disabled={loading}
            variant="outline"
          >
            {loading ? 'Loading...' : 'Load More'}
          </Button>
        </div>
      )}

      {/* No Results */}
      {sections.length === 0 && !loading && (
        <div className="text-center py-8 text-gray-500">
          No sections found. Try adjusting your search or filters.
        </div>
      )}
    </div>
  );
}