"use client";

import React, { useState, useMemo } from "react";
import { 
  Copy, 
  Download, 
  Eye, 
  FileText, 
  Share2, 
  Sparkles, 
  Clock, 
  BarChart3,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Maximize2,
  Minimize2
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";

interface ContentMetadata {
  processing_time_ms?: number;
  word_count?: number;
  content_quality?: number;
  innovation_report?: {
    techniques_used?: string[];
    innovation_level?: string;
    creative_risk_score?: number;
  };
  template_used?: string;
  style_profile_used?: string;
  generation_mode?: string;
  content_extraction_method?: string;
  reading_time_minutes?: number;
}

interface GeneratedContentDisplayProps {
  generatedContent: string;
  isLoading: boolean;
  error?: string | null;
  metadata?: ContentMetadata;
  onRegenerate?: () => void;
  onEdit?: (content: string) => void;
}

export default function GeneratedContentDisplay({
  generatedContent,
  isLoading,
  error = null,
  metadata = {},
  onRegenerate,
  onEdit,
}: GeneratedContentDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState("content");
  const [copySuccess, setCopySuccess] = useState(false);

  // Safe content processing
  const safeTrimmed = useMemo(() => {
    return typeof generatedContent === "string" ? generatedContent.trim() : "";
  }, [generatedContent]);

  // Content analytics
  const contentAnalytics = useMemo(() => {
    if (!safeTrimmed) return null;

    const words = safeTrimmed.split(/\s+/).filter(word => word.length > 0);
    const sentences = safeTrimmed.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const paragraphs = safeTrimmed.split(/\n\s*\n/).filter(p => p.trim().length > 0);
    const characters = safeTrimmed.length;
    const charactersNoSpaces = safeTrimmed.replace(/\s/g, '').length;
    const averageWordsPerSentence = sentences.length > 0 ? Math.round(words.length / sentences.length) : 0;
    const readingTime = Math.max(1, Math.ceil(words.length / 200)); // 200 WPM average

    return {
      wordCount: words.length,
      sentenceCount: sentences.length,
      paragraphCount: paragraphs.length,
      characterCount: characters,
      characterCountNoSpaces: charactersNoSpaces,
      averageWordsPerSentence,
      readingTime,
      contentScore: Math.min(100, Math.round((words.length / 10) + (sentences.length / 2)))
    };
  }, [safeTrimmed]);

  // Markdown to HTML conversion (basic)
  const formatContent = (content: string): string => {
    return content
      // Headers
      .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold mt-6 mb-3 text-gray-900">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-xl font-semibold mt-8 mb-4 text-gray-900">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-8 mb-6 text-gray-900">$1</h1>')
      // Bold and italic
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      // Lists
      .replace(/^\* (.*$)/gim, '<li class="ml-4 mb-1">• $1</li>')
      .replace(/^- (.*$)/gim, '<li class="ml-4 mb-1">• $1</li>')
      // Paragraphs
      .replace(/\n\s*\n/g, '</p><p class="mb-4">')
      // Wrap in paragraphs
      .replace(/^(.*)$/gim, '<p class="mb-4">$1</p>')
      // Clean up empty paragraphs
      .replace(/<p class="mb-4"><\/p>/g, '');
  };

  // Copy to clipboard
  const handleCopy = async () => {
    if (!safeTrimmed) return;
    
    try {
      await navigator.clipboard.writeText(safeTrimmed);
      setCopySuccess(true);
      toast.success("Content copied to clipboard!");
      setTimeout(() => setCopySuccess(false), 2000);
    } catch {
      toast.error("Failed to copy content");
    }
  };

  // Download as file
  const handleDownload = () => {
    if (!safeTrimmed) return;
    
    const blob = new Blob([safeTrimmed], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `generated-content-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("Content downloaded successfully!");
  };

  // Share content
  const handleShare = async () => {
    if (!safeTrimmed) return;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Generated Content',
          text: safeTrimmed.substring(0, 200) + '...',
          url: window.location.href,
        });
      } catch {
        handleCopy(); // Fallback to copy
      }
    } else {
      handleCopy(); // Fallback to copy
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <section className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-blue-600" />
            Generated Content
          </h2>
        </div>
        
        <Card className="shadow-sm">
          <CardContent className="p-8">
            <div className="flex flex-col items-center justify-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              <div className="text-center">
                <p className="text-lg font-medium text-gray-900 mb-2">Generating your content...</p>
                <p className="text-sm text-gray-600">
                  Our AI agents are working together to create high-quality content for you.
                </p>
              </div>
              <Progress value={75} className="w-full max-w-xs" />
            </div>
          </CardContent>
        </Card>
      </section>
    );
  }

  // Error state
  if (error) {
    return (
      <section className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
            <AlertCircle className="h-6 w-6 text-red-600" />
            Generation Error
          </h2>
        </div>
        
        <Card className="shadow-sm border-red-200">
          <CardContent className="p-6">
            <div className="flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-red-900 mb-1">Content generation failed</h3>
                <p className="text-sm text-red-700 mb-4">{error}</p>
                {onRegenerate && (
                  <Button onClick={onRegenerate} variant="outline" size="sm">
                    Try Again
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    );
  }

  // Empty state
  if (!safeTrimmed) {
    return (
      <section className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
            <FileText className="h-6 w-6 text-gray-600" />
            Generated Content
          </h2>
        </div>
        
        <Card className="shadow-sm">
          <CardContent className="p-8">
            <div className="text-center">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No content yet</h3>
              <p className="text-gray-600">
                Select a template and style profile to generate content.
              </p>
            </div>
          </CardContent>
        </Card>
      </section>
    );
  }

  // Main content display
  return (
    <section className="mt-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
          <CheckCircle2 className="h-6 w-6 text-green-600" />
          Generated Content
          {contentAnalytics && (
            <Badge variant="secondary" className="ml-2">
              {contentAnalytics.wordCount} words
            </Badge>
          )}
        </h2>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="hidden sm:flex"
          >
            {isExpanded ? (
              <>
                <Minimize2 className="h-4 w-4 mr-2" />
                Collapse
              </>
            ) : (
              <>
                <Maximize2 className="h-4 w-4 mr-2" />
                Expand
              </>
            )}
          </Button>
        </div>
      </div>

      <Card className={`shadow-sm transition-all duration-300 ${isExpanded ? 'fixed inset-4 z-50 overflow-auto' : ''}`}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <CardTitle className="text-lg">Content Preview</CardTitle>
              {metadata?.generation_mode && (
                <Badge variant="outline" className="text-xs">
                  {metadata.generation_mode}
                </Badge>
              )}
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCopy}
                className="hover:bg-gray-100"
              >
                {copySuccess ? (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDownload}
                className="hover:bg-gray-100"
              >
                <Download className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleShare}
                className="hover:bg-gray-100"
              >
                <Share2 className="h-4 w-4" />
              </Button>
              {onEdit && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onEdit(safeTrimmed)}
                >
                  Edit
                </Button>
              )}
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <div className="px-6 pb-3">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="content" className="flex items-center gap-2">
                  <Eye className="h-4 w-4" />
                  Content
                </TabsTrigger>
                <TabsTrigger value="analytics" className="flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Analytics
                </TabsTrigger>
                <TabsTrigger value="metadata" className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Details
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="content" className="mt-0">
              <div className="px-6 pb-6">
                <div 
                  className="prose prose-neutral max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-li:text-gray-700"
                  dangerouslySetInnerHTML={{ __html: formatContent(safeTrimmed) }}
                />
              </div>
            </TabsContent>

            <TabsContent value="analytics" className="mt-0">
              <div className="px-6 pb-6 space-y-4">
                {contentAnalytics && (
                  <>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-700">{contentAnalytics.wordCount}</div>
                        <div className="text-xs text-blue-600">Words</div>
                      </div>
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-700">{contentAnalytics.sentenceCount}</div>
                        <div className="text-xs text-green-600">Sentences</div>
                      </div>
                      <div className="text-center p-3 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-700">{contentAnalytics.paragraphCount}</div>
                        <div className="text-xs text-purple-600">Paragraphs</div>
                      </div>
                      <div className="text-center p-3 bg-orange-50 rounded-lg">
                        <div className="text-2xl font-bold text-orange-700">{contentAnalytics.readingTime}m</div>
                        <div className="text-xs text-orange-600">Reading Time</div>
                      </div>
                    </div>

                    <Separator />

                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Content Quality Score</span>
                        <span className="text-sm text-gray-600">{contentAnalytics.contentScore}/100</span>
                      </div>
                      <Progress value={contentAnalytics.contentScore} className="h-2" />
                      
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Average words per sentence</span>
                        <span className="text-sm font-medium">{contentAnalytics.averageWordsPerSentence}</span>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">Character count</span>
                        <span className="text-sm font-medium">{contentAnalytics.characterCount.toLocaleString()}</span>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </TabsContent>

            <TabsContent value="metadata" className="mt-0">
              <div className="px-6 pb-6 space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {metadata?.processing_time_ms && (
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm font-medium">Processing Time</span>
                      <span className="text-sm text-gray-600">{(metadata.processing_time_ms / 1000).toFixed(1)}s</span>
                    </div>
                  )}
                  
                  {metadata?.template_used && (
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm font-medium">Template</span>
                      <Badge variant="secondary" className="text-xs">
                        {metadata.template_used}
                      </Badge>
                    </div>
                  )}
                  
                  {metadata?.style_profile_used && (
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm font-medium">Style Profile</span>
                      <Badge variant="secondary" className="text-xs">
                        {metadata.style_profile_used}
                      </Badge>
                    </div>
                  )}
                  
                  {metadata?.content_extraction_method && (
                    <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm font-medium">Extraction Method</span>
                      <Badge variant="outline" className="text-xs">
                        {metadata.content_extraction_method}
                      </Badge>
                    </div>
                  )}
                </div>

                {metadata?.innovation_report && (
                  <div className="mt-6">
                    <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-purple-600" />
                      Innovation Report
                    </h4>
                    <div className="space-y-3">
                      {metadata.innovation_report.innovation_level && (
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Innovation Level</span>
                          <Badge variant="outline" className="text-xs">
                            {metadata.innovation_report.innovation_level}
                          </Badge>
                        </div>
                      )}
                      
                      {metadata.innovation_report.creative_risk_score !== undefined && (
                        <div className="space-y-1">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-600">Creative Risk Score</span>
                            <span className="text-sm font-medium">
                              {(metadata.innovation_report.creative_risk_score * 100).toFixed(0)}%
                            </span>
                          </div>
                          <Progress 
                            value={metadata.innovation_report.creative_risk_score * 100} 
                            className="h-2" 
                          />
                        </div>
                      )}
                      
                      {metadata.innovation_report.techniques_used && metadata.innovation_report.techniques_used.length > 0 && (
                        <div>
                          <span className="text-sm text-gray-600 block mb-2">Techniques Used</span>
                          <div className="flex flex-wrap gap-1">
                            {metadata.innovation_report.techniques_used.map((technique, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {technique}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Action buttons for mobile */}
      <div className="mt-4 flex justify-center space-x-2 sm:hidden">
        <Button
          variant="outline"
          size="sm"
          onClick={handleCopy}
          className="flex-1"
        >
          <Copy className="h-4 w-4 mr-2" />
          Copy
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={handleDownload}
          className="flex-1"
        >
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
        {onRegenerate && (
          <Button
            variant="outline"
            size="sm"
            onClick={onRegenerate}
            className="flex-1"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            Regenerate
          </Button>
        )}
      </div>
    </section>
  );
}