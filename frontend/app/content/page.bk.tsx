// frontend/app/content/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Loader2, FileText, Plus, Filter, Search } from 'lucide-react';
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
};

export default function MyContentPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [contentList, setContentList] = useState<ContentItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Simulate fetch - replace with real API call
    setTimeout(() => {
      setContentList([
        { 
          id: 'intro-contrastive-learning', 
          title: 'Introduction to Contrastive Learning', 
          date: '2025-06-01',
          status: 'published',
          type: 'article'
        },
        { 
          id: 'federated-learning-101', 
          title: 'Federated Learning 101', 
          date: '2025-06-05',
          status: 'draft',
          type: 'guide'
        },
        { 
          id: 'future-of-llms', 
          title: 'Future of LLMs', 
          date: '2025-06-10',
          status: 'published',
          type: 'analysis'
        },
        { 
          id: 'startup-usecases', 
          title: 'Startup Use Cases', 
          date: '2025-06-12',
          status: 'draft',
          type: 'report'
        },
      ]);
      setIsLoading(false);
    }, 1000);
  }, []);

  const filteredContent = contentList.filter(item =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
          <Button variant="outline" size="sm" className="border-purple-400 text-purple-300 hover:bg-purple-900/20">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button asChild className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
            <Link href="/generate" className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              New Content
            </Link>
          </Button>
        </div>
      </div>

      {/* Content Display */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-purple-400" />
        </div>
      ) : filteredContent.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-16 w-16 text-gray-500 mx-auto mb-4" />
          <p className="text-xl text-gray-400 mb-2">
            {searchTerm ? 'No content matches your search' : "You haven't generated anything yet"}
          </p>
          <p className="text-gray-500 mb-6">
            {searchTerm ? 'Try adjusting your search terms' : 'Start creating amazing content with our AI tools'}
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
                <div className="text-2xl font-bold text-white">{contentList.length}</div>
                <p className="text-sm text-gray-300">Total Content</p>
              </CardContent>
            </Card>
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-white">
                  {contentList.filter(item => item.status === 'published').length}
                </div>
                <p className="text-sm text-gray-300">Published</p>
              </CardContent>
            </Card>
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-white">
                  {contentList.filter(item => item.status === 'draft').length}
                </div>
                <p className="text-sm text-gray-300">Drafts</p>
              </CardContent>
            </Card>
            <Card className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardContent className="p-4">
                <div className="text-2xl font-bold text-white">
                  {new Set(contentList.map(item => item.type)).size}
                </div>
                <p className="text-sm text-gray-300">Content Types</p>
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
                    </div>
                    
                    <div className="flex gap-2">
                      <Button asChild size="sm" className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600">
                        <Link href={`/content/${item.id}`}>
                          View Content
                        </Link>
                      </Button>
                      <Button variant="outline" size="sm" className="border-purple-400 text-purple-300 hover:bg-purple-900/20">
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