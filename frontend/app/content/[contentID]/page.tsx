// frontend/app/content/[contentID]/page.tsx
"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowLeft, 
  Edit3, 
  Share2, 
  Download, 
  Eye, 
  Calendar, 
  BarChart3,
  FileText,
  Loader2,
  AlertCircle
} from "lucide-react";

interface ContentData {
  id: string;
  title: string;
  content: string;
  contentHtml?: string;
  status: 'draft' | 'published';
  type: string;
  createdAt: string;
  updatedAt: string;
  views?: number;
  author?: string;
  metadata?: {
    template?: string;
    styleProfile?: string;
    wordCount?: number;
    readingTime?: number;
    [key: string]: unknown;
  };
  week?: string;
}

export default function ContentViewPage() {
  const params = useParams();
  const router = useRouter();
  
  const [content, setContent] = useState<ContentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const contentId = params.contentID as string;

  useEffect(() => {
    const loadContent = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`/api/content/${contentId}`);
        
        if (!response.ok) {
          if (response.status === 404) {
            setError('Content not found');
            return;
          }
          throw new Error(`Failed to load content: ${response.status}`);
        }
        
        const data: ContentData = await response.json();
        setContent(data);
        
      } catch (err) {
        console.error('Error loading content:', err);
        setError(err instanceof Error ? err.message : 'Failed to load content');
      } finally {
        setLoading(false);
      }
    };

    if (contentId) {
      loadContent();
    }
  }, [contentId]);

  const handleEdit = () => {
    router.push(`/content/${contentId}/edit`);
  };

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      // You could add a toast notification here
      alert('Link copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy link:', err);
    }
  };

  const handleExport = (format: 'markdown' | 'html') => {
    if (!content) return;

    let exportContent = content.content;
    const fileName = `${content.title.toLowerCase().replace(/[^a-z0-9]/g, '_')}.${format}`;
    let mimeType = 'text/plain';

    if (format === 'html') {
      exportContent = `<!DOCTYPE html>
<html>
<head>
  <title>${content.title}</title>
  <meta charset="UTF-8">
  <style>
    body { 
      font-family: Georgia, serif; 
      max-width: 800px; 
      margin: 0 auto; 
      padding: 2rem; 
      line-height: 1.6; 
      color: #333;
    }
    h1 { 
      color: #1a202c; 
      border-bottom: 2px solid #667eea; 
      padding-bottom: 0.5rem; 
    }
    h2 { 
      color: #2d3748; 
      margin-top: 2rem; 
    }
    p { 
      margin-bottom: 1rem; 
      text-align: justify; 
    }
    .metadata {
      background: #f7fafc;
      padding: 1rem;
      border-radius: 8px;
      margin: 2rem 0;
      border-left: 4px solid #667eea;
    }
  </style>
</head>
<body>
  <div class="metadata">
    <strong>Title:</strong> ${content.title}<br>
    <strong>Status:</strong> ${content.status}<br>
    <strong>Created:</strong> ${new Date(content.createdAt).toLocaleDateString()}<br>
    ${content.author ? `<strong>Author:</strong> ${content.author}<br>` : ''}
  </div>
  
  ${convertMarkdownToHTML(content.content)}
</body>
</html>`;
      mimeType = 'text/html';
    }

    const blob = new Blob([exportContent], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const convertMarkdownToHTML = (markdown: string): string => {
    return markdown
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(?!<[uo]l>|<h[1-6]>)(.+)$/gm, '<p>$1</p>');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading content...</p>
        </div>
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Content Not Found</h3>
              <p className="text-gray-600 mb-4">{error || 'Content not found'}</p>
              <div className="flex gap-2 justify-center">
                <Button 
                  variant="outline" 
                  onClick={() => router.back()}
                  className="bg-white hover:bg-gray-50 border-gray-300 text-gray-700"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Go Back
                </Button>
                <Button 
                  onClick={() => router.push('/content')}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  View All Content
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            onClick={() => router.back()}
            className="hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl font-bold">{content.title}</h1>
              <Badge variant={content.status === 'published' ? 'default' : 'secondary'}>
                {content.status}
              </Badge>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                <span>Created {formatDate(content.createdAt)}</span>
              </div>
              {content.views !== undefined && (
                <div className="flex items-center gap-1">
                  <Eye className="h-4 w-4" />
                  <span>{content.views} views</span>
                </div>
              )}
              <div className="flex items-center gap-1">
                <FileText className="h-4 w-4" />
                <span>{content.type}</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* ✅ FIXED: Better button styling with explicit variants and colors */}
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            onClick={handleShare}
            className="bg-white hover:bg-gray-50 border-gray-300 text-gray-700"
          >
            <Share2 className="h-4 w-4 mr-2" />
            Share
          </Button>
          <Button 
            variant="outline" 
            onClick={() => handleExport('markdown')}
            className="bg-white hover:bg-gray-50 border-gray-300 text-gray-700"
          >
            <Download className="h-4 w-4 mr-2" />
            Export MD
          </Button>
          <Button 
            variant="outline" 
            onClick={() => handleExport('html')}
            className="bg-white hover:bg-gray-50 border-gray-300 text-gray-700"
          >
            <Download className="h-4 w-4 mr-2" />
            Export HTML
          </Button>
          <Button 
            onClick={handleEdit}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            <Edit3 className="h-4 w-4 mr-2" />
            Edit
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-3">
          <Card>
            <CardContent className="p-8">
              <div 
                className="prose prose-lg max-w-none"
                style={{
                  fontFamily: 'Georgia, "Times New Roman", serif',
                  lineHeight: '1.8',
                  fontSize: '1.1rem'
                }}
                dangerouslySetInnerHTML={{ 
                  __html: convertMarkdownToHTML(content.content) 
                }}
              />
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Content Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Content Statistics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="text-sm font-medium">Words</label>
                <p className="text-sm text-gray-600">
                  {content.content.split(/\s+/).filter(word => word.length > 0).length}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">Characters</label>
                <p className="text-sm text-gray-600">{content.content.length}</p>
              </div>
              <div>
                <label className="text-sm font-medium">Reading Time</label>
                <p className="text-sm text-gray-600">
                  {Math.ceil(content.content.split(/\s+/).filter(word => word.length > 0).length / 200)} min
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">Last Updated</label>
                <p className="text-sm text-gray-600">{formatDate(content.updatedAt)}</p>
              </div>
            </CardContent>
          </Card>

          {/* Metadata */}
          <Card>
            <CardHeader>
              <CardTitle>Metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="text-sm font-medium">Type</label>
                <p className="text-sm text-gray-600">{content.type}</p>
              </div>
              {content.metadata?.template && (
                <div>
                  <label className="text-sm font-medium">Template</label>
                  <p className="text-sm text-gray-600">{content.metadata.template}</p>
                </div>
              )}
              {content.metadata?.styleProfile && (
                <div>
                  <label className="text-sm font-medium">Style Profile</label>
                  <p className="text-sm text-gray-600">{content.metadata.styleProfile}</p>
                </div>
              )}
              {content.author && (
                <div>
                  <label className="text-sm font-medium">Author</label>
                  <p className="text-sm text-gray-600">{content.author}</p>
                </div>
              )}
              {content.week && (
                <div>
                  <label className="text-sm font-medium">Collection</label>
                  <p className="text-sm text-gray-600">{content.week}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}