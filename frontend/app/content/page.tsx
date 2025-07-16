// frontend/app/content/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Loader2, FileText, Plus, Search, AlertCircle, Edit } from 'lucide-react';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

type ContentItem = {
  id: string;
  title: string;
  date: string;
  status: 'draft' | 'published';
  type: string;
  views?: number;
  updatedAt?: string;
  createdAt?: string;
  week?: string;
};

type ContentResponse = {
  content: ContentItem[];
  totalViews: number;
  stats: {
    total: number;
    published: number;
    drafts: number;
    types: number;
  };
};

// Environment configuration
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
const USE_BACKEND_API = process.env.NEXT_PUBLIC_USE_BACKEND_API === 'true';

// Custom hook for content data
function useContentData() {
  const [contentData, setContentData] = useState<ContentResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchContent = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Try frontend API first
      const response = await fetch('/api/content', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404 && USE_BACKEND_API) {
          // Fallback to backend API
          const backendResponse = await fetch(`${BACKEND_URL}/api/content`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (!backendResponse.ok) {
            throw new Error(`Backend API error: ${backendResponse.status}`);
          }

          const backendData = await backendResponse.json();
          setContentData(backendData);
          return;
        }
        throw new Error(`Failed to fetch content: ${response.status}`);
      }

      const data = await response.json();
      setContentData(data);

    } catch (err) {
      console.error('Content fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load content');
      
      // Set empty fallback data
      setContentData({
        content: [],
        totalViews: 0,
        stats: {
          total: 0,
          published: 0,
          drafts: 0,
          types: 0
        }
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchContent();
  }, []);

  return { contentData, isLoading, error, refresh: fetchContent };
}

export default function MyContentPage() {
  const router = useRouter();
  const { contentData, isLoading, error } = useContentData();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'published' | 'draft'>('all');

  // Handle edit content navigation
  const handleEditContent = (contentId: string) => {
    router.push(`/content/${contentId}/edit`);
  };

  // Filter content based on search and status
  const filteredContent = contentData?.content?.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || item.status === filterStatus;
    return matchesSearch && matchesStatus;
  }) || [];

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 space-y-8 text-white">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
            My Generated Content
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            Access, review, and publish your saved AI-generated drafts.
          </p>
        </div>
        <div className="flex justify-center py-12">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-purple-400 mx-auto mb-4" />
            <p className="text-gray-300">Loading your content...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6 space-y-8 text-white">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
            My Generated Content
          </h1>
        </div>
        <div className="flex justify-center py-12">
          <Card className="bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800 max-w-md">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 text-red-700 dark:text-red-300">
                <AlertCircle className="h-5 w-5" />
                <div>
                  <h3 className="font-medium">Failed to load content</h3>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              </div>
              <Button 
                variant="outline" 
                className="mt-4 w-full" 
                onClick={() => window.location.reload()}
              >
                Retry
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const stats = contentData!.stats;

  return (
    <div className="container mx-auto p-6 space-y-8 text-white">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-green-400 bg-clip-text text-transparent">
          My Generated Content
        </h1>
        <p className="text-lg text-gray-300 max-w-2xl mx-auto">
          Access, review, and publish your saved AI-generated drafts.
        </p>
      </div>

      {/* Search and Filter Bar */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search content..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-gray-400"
          />
        </div>
        
        <div className="flex gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as 'all' | 'published' | 'draft')}
            className="px-3 py-2 text-sm bg-white/10 border border-white/20 rounded-md text-white"
          >
            <option value="all">All Status</option>
            <option value="published">Published</option>
            <option value="draft">Drafts</option>
          </select>
          <Button asChild className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
            <Link href="/generate" className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              New Content
            </Link>
          </Button>
        </div>
      </div>

      {/* Content Display */}
      {filteredContent.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-16 w-16 text-gray-500 mx-auto mb-4" />
          <p className="text-xl text-gray-400 mb-2">
            {searchTerm || filterStatus !== 'all' 
              ? 'No content matches your filters' 
              : "You haven't generated anything yet"}
          </p>
          <p className="text-gray-500 mb-6">
            {searchTerm || filterStatus !== 'all'
              ? 'Try adjusting your search terms or filters'
              : 'Start creating amazing content with our AI tools'}
          </p>
          <Button asChild className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
            <Link href="/generate">
              <Plus className="h-4 w-4 mr-2" />
              Create Your First Content
            </Link>
          </Button>
        </div>
      ) : (
        <>
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-white">{stats.total}</div>
                <p className="text-sm text-gray-300">Total Content</p>
              </CardContent>
            </Card>
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-white">{stats.published}</div>
                <p className="text-sm text-gray-300">Published</p>
              </CardContent>
            </Card>
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-white">{stats.drafts}</div>
                <p className="text-sm text-gray-300">Drafts</p>
              </CardContent>
            </Card>
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-white">{contentData!.totalViews.toLocaleString()}</div>
                <p className="text-sm text-gray-300">Total Views</p>
              </CardContent>
            </Card>
          </div>

          {/* Content Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContent.map((item) => (
              <Card key={item.id} className="bg-white/10 backdrop-blur-sm border-white/20 hover:bg-white/15 transition-colors">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="flex items-center gap-2 text-white">
                        <FileText className="h-5 w-5 text-purple-400" />
                        {item.title}
                      </CardTitle>
                      <CardDescription className="text-gray-300 mt-1">
                        Created on {new Date(item.date).toLocaleDateString()}
                        {item.week && (
                          <span className="block text-xs text-gray-400 mt-1">
                            Week: {item.week}
                          </span>
                        )}
                      </CardDescription>
                    </div>
                    <Badge 
                      variant={item.status === 'published' ? 'default' : 'secondary'}
                      className={
                        item.status === 'published'
                          ? 'bg-green-600/20 text-green-300 border border-green-600/30'
                          : 'bg-yellow-600/20 text-yellow-300 border border-yellow-600/30'
                      }
                    >
                      {item.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="border-purple-400/50 text-purple-300">
                        {item.type}
                      </Badge>
                      {item.views && (
                        <span className="text-xs text-gray-400">
                          {item.views} views
                        </span>
                      )}
                    </div>
                    
                    <div className="flex gap-2">
                      <Button asChild size="sm" className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
                        <Link href={`/content/${item.id}`}>
                          View Content
                        </Link>
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => handleEditContent(item.id)}
                        className="border-purple-400 text-purple-300 hover:bg-purple-900/20"
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}