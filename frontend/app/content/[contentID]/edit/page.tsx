// frontend/app/content/[contentID]/edit/page.tsx
'use client';

import { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Save, 
  ArrowLeft, 
  FileText, 
  Download,
  Eye,
  Loader2,
  AlertCircle,
  Copy,
  Check
} from 'lucide-react';
import { toast } from 'sonner';

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
    wordCount?: number;
    readingTime?: number;
    [key: string]: unknown;
  };
  week?: string;
}

export default function EditContentPage() {
  const router = useRouter();
  const params = useParams();
  const contentId = params.contentID as string;

  // Content state
  const [content, setContent] = useState<ContentData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [isPreview, setIsPreview] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  // Form state
  const [editedTitle, setEditedTitle] = useState('');
  const [editedContent, setEditedContent] = useState('');
  const [editedStatus, setEditedStatus] = useState<'draft' | 'published'>('draft');

  // Export menu portal state
  const [showExport, setShowExport] = useState(false);
  const exportBtnRef = useRef<HTMLButtonElement | null>(null);
  const [exportMenuPos, setExportMenuPos] = useState<{ top: number; left: number } | null>(null);

  useEffect(() => {
    if (!showExport) return;
    const onDown = (e: MouseEvent) => {
      const target = e.target as Node;
      const menu = document.getElementById('export-menu-portal');
      if (menu && !menu.contains(target) && !exportBtnRef.current?.contains(target)) {
        setShowExport(false);
      }
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setShowExport(false);
    };
    document.addEventListener('mousedown', onDown);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDown);
      document.removeEventListener('keydown', onKey);
    };
  }, [showExport]);

  // Fetch content data
  useEffect(() => {
    const fetchContent = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`/api/content/${contentId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch content: ${response.status}`);
        }
        const data: ContentData = await response.json();
        setContent(data);
        setEditedTitle(data.title);
        setEditedContent(data.content);
        setEditedStatus(data.status);
      } catch (err) {
        console.error('Error fetching content:', err);
        setError(err instanceof Error ? err.message : 'Failed to load content');
      } finally {
        setIsLoading(false);
      }
    };

    if (contentId) fetchContent();
  }, [contentId]);

  // Track changes
  useEffect(() => {
    if (content) {
      const hasContentChanges = 
        editedTitle !== content.title ||
        editedContent !== content.content ||
        editedStatus !== content.status;
      setHasChanges(hasContentChanges);
    }
  }, [editedTitle, editedContent, editedStatus, content]);

  const handleSave = async () => {
    if (!content || !hasChanges) return;
    
    setIsSaving(true);
    try {
      const response = await fetch(`/api/content/${contentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: editedTitle,
          content: editedContent,
          status: editedStatus,
        }),
      });
    
      if (!response.ok) throw new Error(`Failed to save content: ${response.status}`);
    
      const updatedContent = await response.json();
      
      // Force update with edited values if API doesn't return them
      setContent({
        ...updatedContent,
        title: editedTitle,
        content: editedContent,
        status: editedStatus,
        updatedAt: new Date().toISOString()
      });
      
      setHasChanges(false);
      toast.success('Content saved successfully!');
    } catch (err) {
      console.error('Error saving content:', err);
      toast.error('Failed to save content');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(editedContent);
      setCopySuccess(true);
      toast.success('Content copied to clipboard!');
      setTimeout(() => setCopySuccess(false), 2000);
    } catch {
      toast.error('Failed to copy content');
    }
  };

  // Note: PDF generation here is a simple stub (no styling). For real PDFs, add jsPDF or html2pdf later.
  const handleExport = (format: 'markdown' | 'txt' | 'html' | 'pdf') => {
    let exportContent = editedContent;
    const fileName = `${editedTitle || 'content'}.${format}`;
    let mimeType = 'text/plain';

    if (format === 'html' || format === 'pdf') {
      // Build a simple HTML shell; if 'pdf' we still download HTML unless a PDF lib is integrated.
      exportContent = `<!DOCTYPE html>
<html>
<head>
  <title>${editedTitle}</title>
  <meta charset="UTF-8">
  <style>
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 800px; 
      margin: 0 auto; 
      padding: 2rem; 
      line-height: 1.6; 
    }
    h1, h2, h3 { color: #2563eb; margin-top: 2rem; }
    p { margin-bottom: 1rem; }
  </style>
</head>
<body>
  <h1>${editedTitle}</h1>
  ${editedContent.split('\n').map(line => 
    line.trim() ? `<p>${line}</p>` : '<br>'
  ).join('\n')}
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
    
    toast.success(`Content exported as ${format.toUpperCase()}`);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 text-white">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-purple-400 mx-auto mb-4" />
            <p className="text-gray-300">Loading content...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className="container mx-auto p-6 text-white">
        <div className="flex items-center justify-center min-h-[400px]">
          <Card className="bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800 max-w-md">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 text-red-700 dark:text-red-300">
                <AlertCircle className="h-5 w-5" />
                <div>
                  <h3 className="font-medium">Error Loading Content</h3>
                  <p className="text-sm mt-1">{error || 'Content not found'}</p>
                </div>
              </div>
              <Button 
                variant="outline" 
                className="mt-4 w-full" 
                onClick={() => router.push('/content')}
              >
                Back to Content
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6 text-white">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button 
            variant="outline" 
            onClick={() => router.push('/content')}
            className="border-white/20 text-white hover:bg-white/10"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Content
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Edit Content</h1>
            <p className="text-gray-400 text-sm">
              Last updated: {new Date(content.updatedAt).toLocaleString()}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setIsPreview(!isPreview)}
            className="border-white/20 text-white hover:bg-white/10"
          >
            <Eye className="h-4 w-4 mr-2" />
            {isPreview ? 'Edit' : 'Preview'}
          </Button>
          {hasChanges && (
            <Button
              onClick={handleSave}
              disabled={isSaving}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
            >
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Content Status & Info */}
      <Card className="bg-white/10 backdrop-blur-sm border-white/20">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Badge 
                variant={content.status === 'published' ? 'default' : 'secondary'}
                className={
                  content.status === 'published'
                    ? 'bg-green-600/20 text-green-300 border border-green-600/30'
                    : 'bg-yellow-600/20 text-yellow-300 border border-yellow-600/30'
                }
              >
                {editedStatus}
              </Badge>
              <span className="text-sm text-gray-300">
                {content.metadata?.wordCount || editedContent.split(/\s+/).length} words
              </span>
              <span className="text-sm text-gray-300">
                {Math.ceil((content.metadata?.wordCount || editedContent.split(/\s+/).length) / 200)} min read
              </span>
            </div>
            
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopy}
                className="border-white/20 text-white hover:bg-white/10"
              >
                {copySuccess ? (
                  <Check className="h-4 w-4 mr-1" />
                ) : (
                  <Copy className="h-4 w-4 mr-1" />
                )}
                {copySuccess ? 'Copied!' : 'Copy'}
              </Button>

              {/* Export trigger + portal menu */}
              <div className="relative">
                <Button
                  ref={exportBtnRef}
                  variant="outline"
                  size="sm"
                  className="border-white/20 text-white hover:bg-white/10"
                  onClick={() => {
                    const btn = exportBtnRef.current;
                    if (!btn) return;
                    const rect = btn.getBoundingClientRect();
                    const menuWidth = 176; // tailwind w-44
                    setExportMenuPos({
                      top: rect.bottom + window.scrollY + 8,         // 8px offset
                      left: rect.right + window.scrollX - menuWidth, // right-align
                    });
                    setShowExport((s) => !s);
                  }}
                >
                  <Download className="h-4 w-4 mr-1" />
                  Export
                </Button>
              </div>

              {showExport && exportMenuPos && createPortal(
                <div
                  id="export-menu-portal"
                  className="fixed bg-gray-900 border border-white/30 rounded-md shadow-2xl w-44 z-[9999]"
                  style={{ top: exportMenuPos.top, left: exportMenuPos.left }}
                >
                  <div className="p-1">
                    <button
                      onClick={() => { handleExport('markdown'); setShowExport(false); }}
                      className="block w-full text-left px-3 py-2 text-sm text-white hover:bg-white/20 rounded"
                    >
                      Markdown (.md)
                    </button>
                    <button
                      onClick={() => { handleExport('html'); setShowExport(false); }}
                      className="block w-full text-left px-3 py-2 text-sm text-white hover:bg-white/20 rounded"
                    >
                      HTML (.html)
                    </button>
                    <button
                      onClick={() => { handleExport('txt'); setShowExport(false); }}
                      className="block w-full text-left px-3 py-2 text-sm text-white hover:bg-white/20 rounded"
                    >
                      Text (.txt)
                    </button>
                    <button
                      onClick={() => { handleExport('pdf'); setShowExport(false); }}
                      className="block w-full text-left px-3 py-2 text-sm text-white hover:bg-white/20 rounded"
                    >
                      PDF (.pdf)
                    </button>
                  </div>
                </div>,
                document.body
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Edit Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2">
          <Card className="bg-white/10 backdrop-blur-sm border-white/20">
            <CardHeader>
              <CardTitle className="text-white">
                {isPreview ? 'Content Preview' : 'Edit Content'}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {!isPreview ? (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Title
                    </label>
                    <Input
                      value={editedTitle}
                      onChange={(e) => setEditedTitle(e.target.value)}
                      className="bg-white/10 border-white/20 text-white"
                      placeholder="Enter content title..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Content
                    </label>
                    <Textarea
                      value={editedContent}
                      onChange={(e) => setEditedContent(e.target.value)}
                      className="min-h-[400px] bg-white/10 border-white/20 text-white font-mono"
                      placeholder="Enter your content..."
                    />
                  </div>
                </>
              ) : (
                <div className="prose prose-invert max-w-none">
                  <h1 className="text-2xl font-bold text-white mb-4">{editedTitle}</h1>
                  <div className="text-gray-200 whitespace-pre-wrap leading-relaxed">
                    {editedContent}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Publishing */}
          <Card className="bg-white/10 backdrop-blur-sm border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Publishing
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Status
                </label>
                <select
                  value={editedStatus}
                  onChange={(e) => setEditedStatus(e.target.value as 'draft' | 'published')}
                  className="w-full bg-white/10 border border-white/20 rounded-md px-3 py-2 text-white"
                >
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                </select>
              </div>
              
              <div className="text-sm text-gray-400">
                <p>Created: {new Date(content.createdAt).toLocaleDateString()}</p>
                {content.views && <p>Views: {content.views}</p>}
              </div>
            </CardContent>
          </Card>

          {/* Content Info */}
          <Card className="bg-white/10 backdrop-blur-sm border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Content Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-300">Words:</span>
                <span className="text-white">{editedContent.split(/\s+/).length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Characters:</span>
                <span className="text-white">{editedContent.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Paragraphs:</span>
                <span className="text-white">{editedContent.split('\n\n').length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Reading Time:</span>
                <span className="text-white">
                  {Math.ceil(editedContent.split(/\s+/).length / 200)} min
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Unsaved Changes Warning */}
      {hasChanges && (
        <div className="fixed bottom-4 right-4 bg-yellow-600 text-white p-4 rounded-lg shadow-lg">
          <p className="text-sm font-medium">You have unsaved changes</p>
          <div className="flex gap-2 mt-2">
            <Button
              size="sm"
              onClick={handleSave}
              disabled={isSaving}
              className="bg-white text-yellow-600 hover:bg-gray-100"
            >
              Save Now
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                if (!content) return;
                setEditedTitle(content.title);
                setEditedContent(content.content);
                setEditedStatus(content.status);
              }}
              className="border-white text-white hover:bg-white/10"
            >
              Discard
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
