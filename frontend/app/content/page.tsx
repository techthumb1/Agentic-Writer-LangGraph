// frontend/app/content/page.tsx
"use client";

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Loader2, FileText, Plus, Search, AlertCircle, Edit, Trash2, Eye, Calendar, RefreshCw } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from "@/hooks/use-toast";
import { PageHeader } from '@/components/PageHeader';

interface ContentItem {
  id: string;
  title: string;
  date: string;
  status: 'draft' | 'published';
  template_type: string;
  views?: number;
  updated_at?: string;
  created_at?: string;
  week?: string;
}

interface ContentResponse {
  content: ContentItem[];
  total_views: number;
  stats: {
    total: number;
    published: number;
    drafts: number;
  };
}

export default function MyContentPage() {
  const router = useRouter();
  const { toast } = useToast();
  
  const [contentData, setContentData] = useState<ContentResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'published' | 'draft'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'title' | 'views'>('date');

  const fetchContent = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch('/api/content', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch content: ${response.status}`);
      }

      const data = await response.json();
      setContentData(data);
      console.log('📋 [CONTENT-PAGE] Loaded content:', data);

    } catch (err) {
      console.error('Content fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load content');
      
      setContentData({
        content: [],
        total_views: 0,
        stats: { total: 0, published: 0, drafts: 0 }
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchContent();
  }, []);

  const handleEditContent = (contentId: string) => {
    router.push(`/content/${contentId}/edit`);
  };

  const handleViewContent = (contentId: string) => {
    router.push(`/content/${contentId}`);
  };

  const handleDeleteContent = async (contentId: string, title: string) => {
    if (!confirm(`Are you sure you want to delete "${title}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`/api/content/${contentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Failed to delete: ${response.status}`);
      }

      toast({
        title: "Content Deleted",
        description: `"${title}" has been deleted successfully.`,
      });

      fetchContent();

    } catch (err) {
      console.error('Error deleting content:', err);
      toast({
        title: "Delete Failed",
        description: err instanceof Error ? err.message : "Failed to delete content",
        variant: "destructive",
      });
    }
  };

  const filteredAndSortedContent = contentData?.content?.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.template_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || item.status === filterStatus;
    return matchesSearch && matchesStatus;
  }).sort((a, b) => {
    switch (sortBy) {
      case 'title':
        return a.title.localeCompare(b.title);
      case 'views':
        return (b.views || 0) - (a.views || 0);
      case 'date':
      default:
        return new Date(b.created_at || b.date).getTime() - new Date(a.created_at || a.date).getTime();
    }
  }) || [];

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRelativeTime = (dateString: string) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));

    if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffMinutes > 0) {
      return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    } else {
      return 'Just now';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen theme-background">
        <div className="container mx-auto p-6 space-y-8">
          <PageHeader
            title="My Generated"
            gradientText="Content"
            subtitle="Access, review, and publish your saved AI-generated drafts."
            size="lg"
          />
          <div className="flex justify-center py-12">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
              <p className="text-muted-foreground">Loading your content...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen theme-background">
        <div className="container mx-auto p-6 space-y-8">
          <PageHeader
            title="My Generated"
            gradientText="Content"
            subtitle="Access, review, and publish your saved AI-generated drafts."
            size="lg"
          />
          <div className="flex justify-center py-12">
            <Card className="theme-card max-w-md">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3 text-destructive">
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
      </div>
    );
  }

  const stats = contentData!.stats;

  return (
    <div className="min-h-screen theme-background">
      <div className="container mx-auto p-6 space-y-8">
        <PageHeader
          title="My Generated"
          gradientText="Content"
          subtitle="Access, review, and publish your saved AI-generated drafts."
          size="lg"
        />

        <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search content..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="flex gap-2">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as 'all' | 'published' | 'draft')}
              className="px-3 py-2 text-sm theme-input rounded-md"
            >
              <option value="all">All Status</option>
              <option value="published">Published</option>
              <option value="draft">Drafts</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'title' | 'views')}
              className="px-3 py-2 text-sm theme-input rounded-md"
            >
              <option value="date">Sort by Date</option>
              <option value="title">Sort by Title</option>
              <option value="views">Sort by Views</option>
            </select>
            <Button 
              variant="outline" 
              size="icon" 
              onClick={fetchContent}
              className="action-btn outline"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button 
              onClick={() => router.push('/generate')}
              className="action-btn primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              New Content
            </Button>
          </div>
        </div>

        {filteredAndSortedContent.length === 0 ? (
          <div className="empty-state">
            <FileText className="empty-state-icon" />
            <h3 className="empty-state-title">
              {searchTerm || filterStatus !== 'all' 
                ? 'No content matches your filters' 
                : "You haven't generated anything yet"}
            </h3>
            <p className="empty-state-description">
              {searchTerm || filterStatus !== 'all'
                ? 'Try adjusting your search terms or filters'
                : 'Start creating amazing content with our AI tools'}
            </p>
            <div className="flex gap-2 justify-center">
              {(searchTerm || filterStatus !== 'all') && (
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setSearchTerm("");
                    setFilterStatus('all');
                  }}
                  className="action-btn outline"
                >
                  Clear Filters
                </Button>
              )}
              <Button 
                onClick={() => router.push('/generate')}
                className="action-btn primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Content
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <Card className="stats-card">
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-foreground">{stats.total}</div>
                  <p className="text-sm text-muted-foreground">Total Content</p>
                </CardContent>
              </Card>
              <Card className="stats-card">
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-foreground">{stats.published}</div>
                  <p className="text-sm text-muted-foreground">Published</p>
                </CardContent>
              </Card>
              <Card className="stats-card">
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-foreground">{stats.drafts}</div>
                  <p className="text-sm text-muted-foreground">Drafts</p>
                </CardContent>
              </Card>
              <Card className="stats-card">
                <CardContent className="p-4">
                  <div className="text-2xl font-bold text-foreground">{contentData!.total_views.toLocaleString()}</div>
                  <p className="text-sm text-muted-foreground">Total Views</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredAndSortedContent.map((item) => (
                <Card key={item.id} className="theme-card">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="flex items-center gap-2 text-foreground">
                          <FileText className="h-5 w-5 text-primary" />
                          {item.title}
                        </CardTitle>
                        <CardDescription className="text-muted-foreground mt-1">
                          Created {getRelativeTime(item.created_at || item.date)}
                          {item.week && (
                            <span className="block text-xs text-muted-foreground mt-1">
                              Week: {item.week}
                            </span>
                          )}
                        </CardDescription>
                      </div>
                      <Badge 
                        variant={item.status === 'published' ? 'default' : 'secondary'}
                        className={`status-badge ${item.status}`}
                      >
                        {item.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="border-primary/50 text-primary">
                          {item.template_type}
                        </Badge>
                        {item.views !== undefined && (
                          <span className="text-xs text-muted-foreground">
                            {item.views} views
                          </span>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          <span>{formatDate(item.updated_at || item.date)}</span>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          className="flex-1 action-btn primary"
                          onClick={() => handleViewContent(item.id)}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => handleEditContent(item.id)}
                          className="action-btn outline"
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Edit
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => handleDeleteContent(item.id, item.title)}
                          className="border-destructive text-destructive hover:bg-destructive/10"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {filteredAndSortedContent.length > 0 && (
              <div className="text-center text-sm text-muted-foreground py-4">
                Showing {filteredAndSortedContent.length} of {contentData?.stats.total || 0} content items
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}