'use client';

import { useState, useEffect } from 'react';
import SectionsTable from '@/components/sections-table';
import { DatabaseStats } from '@/lib/db';

export default function Home() {
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [healthStatus, setHealthStatus] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    // Check database health
    fetch('/api/health')
      .then(res => res.json())
      .then(data => {
        setHealthStatus(data.status === 'healthy' ? 'healthy' : 'unhealthy');
      })
      .catch(() => setHealthStatus('unhealthy'));

    // Fetch database statistics
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => {
        setStats(data);
        setLoadingStats(false);
      })
      .catch(error => {
        console.error('Failed to fetch stats:', error);
        setLoadingStats(false);
      });
  }, []);

  const getHealthBadge = () => {
    switch (healthStatus) {
      case 'healthy':
        return <span className="inline-block px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Connected</span>;
      case 'unhealthy':
        return <span className="inline-block px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">Disconnected</span>;
      default:
        return <span className="inline-block px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Checking...</span>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">ECMA-376 Database Viewer</h1>
              <p className="text-gray-600 mt-1">Browse and search ECMA-376 documentation sections</p>
            </div>
            <div className="mt-4 sm:mt-0 flex items-center gap-2">
              <span className="text-sm text-gray-600">Database:</span>
              {getHealthBadge()}
            </div>
          </div>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">Total Sections</h3>
              <p className="text-2xl font-bold text-gray-900">{stats.general.total_sections.toLocaleString()}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">With Embeddings</h3>
              <p className="text-2xl font-bold text-gray-900">{stats.general.sections_with_embeddings.toLocaleString()}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">Depth Levels</h3>
              <p className="text-2xl font-bold text-gray-900">{Object.keys(stats.depth_distribution).length}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-sm font-medium text-gray-500">Section Types</h3>
              <p className="text-2xl font-bold text-gray-900">{Object.keys(stats.type_distribution).length}</p>
            </div>
          </div>
        )}

        {/* Loading Stats */}
        {loadingStats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-white p-6 rounded-lg shadow animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-16"></div>
              </div>
            ))}
          </div>
        )}

        {/* Database Connection Error */}
        {healthStatus === 'unhealthy' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Database Connection Error</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>Unable to connect to the PostgreSQL database. Please ensure:</p>
                  <ul className="list-disc list-inside mt-1 space-y-1">
                    <li>PostgreSQL is running on localhost:5432</li>
                    <li>Database &apos;ecma376_docs&apos; exists</li>
                    <li>User &apos;thomasjeon&apos; has access permissions</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">ECMA Sections</h2>
            {healthStatus === 'healthy' ? (
              <SectionsTable />
            ) : (
              <div className="text-center py-8 text-gray-500">
                Database connection required to view sections.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
