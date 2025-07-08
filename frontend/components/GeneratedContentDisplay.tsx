// File: frontend/components/GeneratedContentDisplay.tsx
// Enterprise-Grade Content Display with Advanced Analytics & AI-Powered Features

import React, { useState, useRef, useCallback, useEffect, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { usePerformanceMonitoring } from '@/hooks/use-performance';
import { useMCP } from '@/hooks/useMCP';
import { 
  Copy, 
  Download, 
  Eye, 
  Save, 
  FileText, 
  Share2, 
  Zap, 
  BarChart3, 
  Brain, 
  Sparkles,
  RefreshCw,
  ExternalLink,
  Settings,
  TrendingUp
} from 'lucide-react';

// Enterprise interfaces
interface ContentAnalytics {
  readability_score: number;
  sentiment_analysis: {
    score: number;
    confidence: number;
    dominant_emotion: string;
  };
  seo_optimization: {
    score: number;
    keyword_density: Record<string, number>;
    suggestions: string[];
  };
  engagement_prediction: {
    score: number;
    viral_potential: number;
    target_demographics: string[];
  };
  competitive_analysis?: {
    uniqueness_score: number;
    market_differentiation: number;
    innovation_index: number;
  };
}

interface EnterpriseMetadata {
  generation_id: string;
  model_used: string;
  tokens_consumed: number;
  generation_time: number;
  cost_analysis: {
    generation_cost: number;
    projected_roi: number;
    monetization_potential: number;
  };
  quality_metrics: {
    coherence_score: number;
    creativity_index: number;
    technical_accuracy: number;
    brand_alignment: number;
  };
  mcp_enhanced?: boolean;
  agent_contributions: Array<{
    agent: string;
    contribution_score: number;
    innovations_added: string[];
  }>;
}

interface GeneratedContentDisplayProps {
  content: string;
  generationId?: string;
  metadata?: EnterpriseMetadata;
  analytics?: ContentAnalytics;
  isLoading?: boolean;
  onContentUpdate?: (updatedContent: string) => void;
  enableRealTimeAnalytics?: boolean;
  enableAIEnhancements?: boolean;
  enableCompetitiveIntelligence?: boolean;
}

const GeneratedContentDisplay: React.FC<GeneratedContentDisplayProps> = ({ 
  content, 
  generationId,
  metadata,
  analytics: initialAnalytics,
  isLoading = false,
  onContentUpdate,
  enableRealTimeAnalytics = true,
  enableAIEnhancements = true,
  enableCompetitiveIntelligence = true
}) => {
  // Enterprise state management
  const [isSaving, setIsSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [analytics, setAnalytics] = useState<ContentAnalytics | null>(initialAnalytics || null);
  const [exportFormat, setExportFormat] = useState<'markdown' | 'html' | 'pdf' | 'docx'>('markdown');
  const [shareableUrl, setShareableUrl] = useState<string | null>(null);
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  
  const { toast } = useToast();
  const { measureFunction, reportMetric } = usePerformanceMonitoring();
  const { mcpCapabilities, callTool, storeMemory } = useMCP();
  const contentRef = useRef<HTMLDivElement>(null);

  // Enterprise content analysis
  const contentStats = useMemo(() => {
    if (!content) return null;
    
    return {
      word_count: content.split(/\s+/).length,
      character_count: content.length,
      paragraph_count: content.split('\n\n').length,
      estimated_read_time: Math.ceil(content.split(/\s+/).length / 200), // 200 WPM average
      complexity_score: calculateComplexityScore(content),
      uniqueness_fingerprint: generateContentFingerprint(content)
    };
  }, [content]);

  // Advanced copy with AI-powered variations
  const handleIntelligentCopy = useCallback(measureFunction(async () => {
    try {
      const copyVariations = [];
      
      // Original content
      copyVariations.push({ type: 'original', content });
      
      // AI-enhanced variations if MCP is available
      if (mcpCapabilities?.research && enableAIEnhancements) {
        try {
          const enhancedContent = await callTool({
            tool_name: 'enhance_content',
            arguments: {
              content,
              enhancement_type: 'clarity_and_engagement',
              preserve_intent: true
            }
          });
          
          if (enhancedContent.success) {
            copyVariations.push({ 
              type: 'enhanced', 
              content: enhancedContent.result as string 
            });
          }
        } catch (error) {
          console.warn('AI enhancement failed:', error);
        }
      }
      
      // Copy with analytics metadata
      const copyData = {
        variations: copyVariations,
        metadata: {
          generation_id: generationId,
          copied_at: new Date().toISOString(),
          content_stats: contentStats,
          analytics: analytics
        }
      };
      
      await navigator.clipboard.writeText(JSON.stringify(copyData, null, 2));
      
      // Store copy action in MCP memory for learning
      if (mcpCapabilities?.memory) {
        await storeMemory({
          key: `copy_action_${generationId}`,
          value: JSON.stringify({
            timestamp: new Date().toISOString(),
            content_fingerprint: contentStats?.uniqueness_fingerprint,
            user_intent: 'copy_for_reuse'
          }),
          namespace: 'user_interactions'
        });
      }
      
      toast({
        title: "Enhanced Copy Complete!",
        description: `Copied ${copyVariations.length} content variations with metadata.`,
      });
      
      reportMetric({
        name: 'content_copy_with_ai',
        value: copyVariations.length,
        timestamp: Date.now()
      });
      
    } catch (error) {
      // Fallback to simple copy
      await navigator.clipboard.writeText(content);
      toast({
        title: "Content Copied",
        description: "Standard copy completed (AI features unavailable).",
      });
    }
  }, 'intelligent_copy'), [content, generationId, mcpCapabilities, analytics, contentStats]);

  // Advanced export with multiple formats and AI optimization
  const handleAdvancedExport = useCallback(measureFunction(async () => {
    setIsExporting(true);
    try {
      let exportContent = content;
      let filename = `content-${generationId || Date.now()}`;
      
      // AI-optimize content for export format if available
      if (enableAIEnhancements && mcpCapabilities?.research) {
        try {
          const optimizedContent = await callTool({
            tool_name: 'optimize_for_format',
            arguments: {
              content,
              target_format: exportFormat,
              optimization_level: 'enterprise'
            }
          });
          
          if (optimizedContent.success) {
            exportContent = optimizedContent.result as string;
          }
        } catch (error) {
          console.warn('Export optimization failed:', error);
        }
      }
      
      // Enhanced export with analytics embedding
      const exportPackage = {
        content: exportContent,
        metadata: {
          ...metadata,
          export_timestamp: new Date().toISOString(),
          export_format: exportFormat,
          content_analytics: analytics,
          performance_metrics: contentStats
        },
        ai_enhancements: {
          mcp_enhanced: mcpCapabilities ? true : false,
          optimization_applied: enableAIEnhancements,
          competitive_analysis: enableCompetitiveIntelligence ? analytics?.competitive_analysis : null
        }
      };
      
      let blob: Blob;
      let fileExtension: string;
      
      switch (exportFormat) {
        case 'markdown':
          blob = new Blob([
            `# ${metadata?.generation_id || 'Generated Content'}\n\n`,
            `**Generated:** ${new Date().toISOString()}\n`,
            `**Analytics Score:** ${analytics?.seo_optimization?.score || 'N/A'}\n\n`,
            `---\n\n`,
            exportContent,
            `\n\n---\n\n`,
            `**Metadata:**\n\`\`\`json\n${JSON.stringify(exportPackage.metadata, null, 2)}\n\`\`\``
          ].join(''), { type: 'text/markdown' });
          fileExtension = 'md';
          break;
          
        case 'html':
          blob = new Blob([`
            <!DOCTYPE html>
            <html>
            <head>
              <title>${metadata?.generation_id || 'Generated Content'}</title>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <style>
                body { 
                  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                  max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; 
                }
                .metadata { 
                  background: #f8fafc; padding: 1rem; border-radius: 0.5rem; 
                  margin: 2rem 0; border: 1px solid #e2e8f0; 
                }
                .analytics-badge {
                  display: inline-block; background: #2563eb; color: white;
                  padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem;
                }
              </style>
            </head>
            <body>
              <div class="analytics-badge">SEO Score: ${analytics?.seo_optimization?.score || 'N/A'}</div>
              <div class="analytics-badge">Readability: ${analytics?.readability_score || 'N/A'}</div>
              ${convertToHTML(exportContent)}
              <div class="metadata">
                <h4>Generation Metadata</h4>
                <pre>${JSON.stringify(exportPackage.metadata, null, 2)}</pre>
              </div>
            </body>
            </html>
          `], { type: 'text/html' });
          fileExtension = 'html';
          break;
          
        case 'pdf':
          // For PDF, we'll create a rich HTML that can be printed to PDF
          blob = new Blob([createPDFContent(exportContent, exportPackage)], { type: 'text/html' });
          fileExtension = 'html'; // User can print to PDF
          filename += '-for-pdf';
          break;
          
        default:
          blob = new Blob([JSON.stringify(exportPackage, null, 2)], { type: 'application/json' });
          fileExtension = 'json';
      }
      
      // Download the file
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${filename}.${fileExtension}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast({
        title: "Export Successful!",
        description: `Content exported as ${exportFormat.toUpperCase()} with analytics.`,
      });
      
      reportMetric({
        name: 'advanced_content_export',
        value: exportContent.length,
        timestamp: Date.now()
      });
      
    } catch (error) {
      console.error('Export failed:', error);
      toast({
        title: "Export Failed",
        description: "Unable to export content with enhancements.",
        variant: "destructive",
      });
    } finally {
      setIsExporting(false);
    }
  }, 'advanced_export'), [content, exportFormat, generationId, metadata, analytics, mcpCapabilities]);

  // AI-powered content analysis
  const handleRealTimeAnalysis = useCallback(measureFunction(async () => {
    if (!enableRealTimeAnalytics) return;
    
    setIsAnalyzing(true);
    try {
      // Multi-layered analysis using different AI models
      const analysisPromises = [];
      
      // Basic analytics via API
      analysisPromises.push(
        fetch('/api/analyze/content', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content,
            analysis_types: ['readability', 'seo', 'sentiment', 'engagement'],
            generation_id: generationId
          })
        }).then(res => res.json())
      );
      
      // Advanced MCP-powered analysis
      if (mcpCapabilities?.research) {
        analysisPromises.push(
          callTool({
            tool_name: 'analyze_content_competitiveness',
            arguments: {
              content,
              industry_context: metadata?.quality_metrics?.brand_alignment,
              competitor_benchmark: true
            }
          })
        );
      }
      
      const [basicAnalysis, mcpAnalysis] = await Promise.allSettled(analysisPromises);
      
      // Combine results
      const combinedAnalytics: ContentAnalytics = {
        readability_score: 0,
        sentiment_analysis: { score: 0, confidence: 0, dominant_emotion: 'neutral' },
        seo_optimization: { score: 0, keyword_density: {}, suggestions: [] },
        engagement_prediction: { score: 0, viral_potential: 0, target_demographics: [] },
        ...(basicAnalysis.status === 'fulfilled' ? basicAnalysis.value : {}),
        ...(mcpAnalysis.status === 'fulfilled' && mcpAnalysis.value.success ? {
          competitive_analysis: mcpAnalysis.value.result as any
        } : {})
      };
      
      setAnalytics(combinedAnalytics);
      
      toast({
        title: "Analysis Complete!",
        description: `Content analyzed with ${analysisPromises.length} AI models.`,
      });
      
    } catch (error) {
      console.error('Analysis failed:', error);
      toast({
        title: "Analysis Failed",
        description: "Unable to complete real-time analysis.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, 'realtime_analysis'), [content, generationId, mcpCapabilities, enableRealTimeAnalytics]);

  // Enterprise content saving with advanced features
  const handleEnterpriseSave = useCallback(measureFunction(async () => {
    setIsSaving(true);
    try {
      const savePayload = {
        title: `Generated Content - ${new Date().toLocaleDateString()}`,
        template: metadata?.generation_id || 'unknown',
        style_profile: 'enterprise',
        content,
        dynamic_parameters: {
          generation_metadata: metadata,
          content_analytics: analytics,
          performance_metrics: contentStats,
          ai_enhancements: {
            mcp_enhanced: metadata?.mcp_enhanced || false,
            quality_score: calculateOverallQuality(analytics, metadata),
            monetization_potential: metadata?.cost_analysis?.monetization_potential || 0
          }
        },
        priority: metadata?.cost_analysis?.projected_roi ? Math.ceil(metadata.cost_analysis.projected_roi * 10) : 1,
        generation_mode: 'enterprise'
      };
      
      const response = await fetch('/api/content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(savePayload),
      });

      if (!response.ok) {
        throw new Error(`Save failed: ${response.status}`);
      }

      const result = await response.json();
      
      // Generate shareable URL for enterprise collaboration
      if (result.success && result.content?.id) {
        const shareUrl = `${window.location.origin}/content/${result.content.id}`;
        setShareableUrl(shareUrl);
      }
      
      toast({
        title: "Enterprise Save Complete!",
        description: `Content saved with analytics and monetization data.`,
      });
      
      reportMetric({
        name: 'enterprise_content_save',
        value: metadata?.cost_analysis?.monetization_potential || 0,
        timestamp: Date.now()
      });
      
    } catch (error) {
      console.error('Save failed:', error);
      toast({
        title: "Save Failed",
        description: "Unable to save content with enterprise features.",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  }, 'enterprise_save'), [content, metadata, analytics, contentStats]);

  // AI-powered content enhancement
  const handleAIEnhancement = useCallback(async () => {
    if (!enableAIEnhancements || !mcpCapabilities?.research) {
      toast({
        title: "AI Enhancement Unavailable",
        description: "MCP research capabilities required.",
        variant: "destructive",
      });
      return;
    }
    
    setIsEnhancing(true);
    try {
      const enhancements = await callTool({
        tool_name: 'enhance_content_enterprise',
        arguments: {
          content,
          enhancement_targets: [
            'engagement_optimization',
            'seo_enhancement', 
            'competitive_differentiation',
            'monetization_optimization'
          ],
          preserve_voice: true,
          target_metrics: {
            min_engagement_score: 85,
            min_seo_score: 90,
            min_uniqueness_score: 95
          }
        }
      });
      
      if (enhancements.success && onContentUpdate) {
        onContentUpdate(enhancements.result as string);
        
        toast({
          title: "AI Enhancement Complete!",
          description: "Content optimized for engagement and monetization.",
        });
      }
      
    } catch (error) {
      console.error('Enhancement failed:', error);
      toast({
        title: "Enhancement Failed",
        description: "AI enhancement could not be completed.",
        variant: "destructive",
      });
    } finally {
      setIsEnhancing(false);
    }
  }, [content, mcpCapabilities, enableAIEnhancements, onContentUpdate]);

  // Auto-analyze on content change
  useEffect(() => {
    if (content && enableRealTimeAnalytics) {
      const timeoutId = setTimeout(handleRealTimeAnalysis, 1000);
      return () => clearTimeout(timeoutId);
    }
  }, [content, handleRealTimeAnalysis]);

  // Enterprise preview with competitive intelligence
  const handleEnterprisePreview = useCallback(() => {
    const previewData = {
      content,
      analytics,
      metadata,
      competitive_intelligence: enableCompetitiveIntelligence ? {
        market_position: analytics?.competitive_analysis?.market_differentiation || 0,
        innovation_score: analytics?.competitive_analysis?.innovation_index || 0,
        monetization_potential: metadata?.cost_analysis?.monetization_potential || 0
      } : null
    };
    
    const previewWindow = window.open('', '_blank', 'width=1200,height=800');
    if (previewWindow) {
      previewWindow.document.write(createEnterprisePreview(previewData));
      previewWindow.document.close();
    }
  }, [content, analytics, metadata, enableCompetitiveIntelligence]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Generating enterprise content...</span>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="text-center p-8 text-gray-500">
        <FileText className="mx-auto h-12 w-12 mb-4 opacity-50" />
        <p>No content generated yet.</p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-6">
      {/* Enterprise Analytics Dashboard */}
      {analytics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {analytics.seo_optimization.score}
            </div>
            <div className="text-sm text-gray-600">SEO Score</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {analytics.engagement_prediction.score}
            </div>
            <div className="text-sm text-gray-600">Engagement</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {analytics.readability_score}
            </div>
            <div className="text-sm text-gray-600">Readability</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {metadata?.cost_analysis?.monetization_potential || 0}
            </div>
            <div className="text-sm text-gray-600">ROI Potential</div>
          </div>
        </div>
      )}

      {/* Enterprise Action Buttons */}
      <div className="flex flex-wrap gap-2 justify-between items-center border-b pb-4">
        <div className="flex flex-wrap gap-2">
          <Button
            onClick={handleIntelligentCopy}
            variant="outline"
            size="sm"
            className="flex items-center gap-2"
          >
            <Copy className="h-4 w-4" />
            Smart Copy
          </Button>
          
          <div className="flex items-center gap-1">
            <Button
              onClick={handleAdvancedExport}
              variant="outline"
              size="sm"
              disabled={isExporting}
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              {isExporting ? 'Exporting...' : 'Export'}
            </Button>
            <select 
              value={exportFormat} 
              onChange={(e) => setExportFormat(e.target.value as any)}
              className="text-xs border rounded px-2 py-1"
            >
              <option value="markdown">MD</option>
              <option value="html">HTML</option>
              <option value="pdf">PDF</option>
            </select>
          </div>
          
          <Button
            onClick={handleEnterprisePreview}
            variant="outline"
            size="sm"
            className="flex items-center gap-2"
          >
            <Eye className="h-4 w-4" />
            Enterprise Preview
          </Button>
        </div>

        <div className="flex flex-wrap gap-2">
          {enableRealTimeAnalytics && (
            <Button
              onClick={handleRealTimeAnalysis}
              variant="outline"
              size="sm"
              disabled={isAnalyzing}
              className="flex items-center gap-2"
            >
              <BarChart3 className="h-4 w-4" />
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </Button>
          )}
          
          {enableAIEnhancements && mcpCapabilities?.research && (
            <Button
              onClick={handleAIEnhancement}
              variant="outline"
              size="sm"
              disabled={isEnhancing}
              className="flex items-center gap-2"
            >
              <Sparkles className="h-4 w-4" />
              {isEnhancing ? 'Enhancing...' : 'AI Enhance'}
            </Button>
          )}
          
          <Button
            onClick={handleEnterpriseSave}
            variant="default"
            size="sm"
            disabled={isSaving}
            className="flex items-center gap-2"
          >
            <Save className="h-4 w-4" />
            {isSaving ? 'Saving...' : 'Save Enterprise'}
          </Button>
        </div>
      </div>

      {/* Content Display with Enterprise Features */}
      <div className="relative">
        <div 
          ref={contentRef}
          className="prose prose-sm max-w-none p-6 bg-white border rounded-lg shadow-sm"
          style={{ 
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            overflowWrap: 'break-word'
          }}
        >
          {content}
        </div>
        
        {/* Real-time quality indicator */}
        {analytics && (
          <div className="absolute top-2 right-2 flex gap-1">
            <div className={`w-3 h-3 rounded-full ${
              analytics.seo_optimization.score > 80 ? 'bg-green-500' : 
              analytics.seo_optimization.score > 60 ? 'bg-yellow-500' : 'bg-red-500'
            }`} title="SEO Quality" />
            <div className={`w-3 h-3 rounded-full ${
              analytics.engagement_prediction.score > 80 ? 'bg-green-500' : 
              analytics.engagement_prediction.score > 60 ? 'bg-yellow-500' : 'bg-red-500'
            }`} title="Engagement Quality" />
          </div>
        )}
      </div>

      {/* Enterprise Metadata Panel */}
      {(metadata || contentStats) && (
        <details className="text-sm border rounded-lg">
          <summary className="cursor-pointer p-3 bg-gray-50 hover:bg-gray-100 rounded-lg">
            Enterprise Analytics & Metadata
          </summary>
          <div className="p-4 space-y-4">
            {contentStats && (
              <div>
                <h4 className="font-semibold mb-2">Content Statistics</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                  <div>Words: {contentStats.word_count}</div>
                  <div>Characters: {contentStats.character_count}</div>
                  <div>Read Time: {contentStats.estimated_read_time}min</div>
                  <div>Complexity: {contentStats.complexity_score}/100</div>
                </div>
              </div>
            )}
            
            {metadata && (
              <div>
                <h4 className="font-semibold mb-2">Generation Metadata</h4>
                <div className="text-xs space-y-1">
                  <div>Model: {metadata.model_used}</div>
                  <div>Tokens: {metadata.tokens_consumed}</div>
                  <div>Generation Time: {metadata.generation_time}ms</div>
                  <div>Cost: ${metadata.cost_analysis.generation_cost}</div>
                  <div>ROI Projection: {metadata.cost_analysis.projected_roi}x</div>
                </div>
              </div>
            )}
          </div>
        </details>
      )}

      {/* Shareable URL */}
      {shareableUrl && (
        <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
          <ExternalLink className="h-4 w-4 text-blue-600" />
          <span className="text-sm font-medium">Shareable URL:</span>
          <input 
            type="text" 
            value={shareableUrl} 
            readOnly 
            className="flex-1 text-xs bg-white border rounded px-2 py-1"
          />
          <Button
            onClick={() => navigator.clipboard.writeText(shareableUrl)}
            size="sm"
            variant="outline"
          >
            Copy Link
          </Button>
        </div>
      )}
    </div>
  );
};

// Helper functions for enterprise features
function calculateComplexityScore(content: string): number {
  const sentences = content.split(/[.!?]+/).length;
  const words = content.split(/\s+/).length;
  const avgWordsPerSentence = words / sentences;
  const longWords = content.split(/\s+/).filter(word => word.length > 6).length;
  const longWordRatio = longWords / words;
  
  return Math.min(100, Math.round((avgWordsPerSentence * 2) + (longWordRatio * 50)));
}

function generateContentFingerprint(content: string): string {
  // Simple hash for content uniqueness tracking
  let hash = 0;
  for (let i = 0; i < content.length; i++) {
    const char = content.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(36);
}

function calculateOverallQuality(analytics: ContentAnalytics | null, metadata: EnterpriseMetadata | undefined): number {
  if (!analytics || !metadata) return 0;
  
  const weights = {
    seo: 0.25,
    engagement: 0.25,
    readability: 0.2,
    technical_accuracy: 0.15,
    creativity: 0.15
  };
  
  return Math.round(
    (analytics.seo_optimization.score * weights.seo) +
    (analytics.engagement_prediction.score * weights.engagement) +
    (analytics.readability_score * weights.readability) +
    (metadata.quality_metrics.technical_accuracy * weights.technical_accuracy) +
    (metadata.quality_metrics.creativity_index * weights.creativity)
  );
}

function convertToHTML(markdown: string): string {
  return markdown
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^\- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    .replace(/^(.+)$/gm, '<p>$1</p>')
    .replace(/<\/p>\s*<ul>/g, '</p><ul>')
    .replace(/<\/ul>\s*<p>/g, '</ul><p>')
    .replace(/\n/g, '<br>');
}

function createPDFContent(content: string, exportPackage: any): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Enterprise Content Export</title>
      <meta charset="UTF-8">
      <style>
        @page { 
          margin: 1in; 
          size: A4;
          @top-center { content: "Enterprise Content - ${exportPackage.metadata.generation_id || 'N/A'}"; }
          @bottom-center { content: counter(page) " of " counter(pages); }
        }
        body { 
          font-family: 'Times New Roman', serif; 
          line-height: 1.6; 
          color: #333; 
          font-size: 12pt;
        }
        h1, h2, h3 { 
          color: #2563eb; 
          page-break-after: avoid; 
          margin-top: 24pt; 
          margin-bottom: 12pt;
        }
        .header { 
          border-bottom: 2px solid #2563eb; 
          padding-bottom: 10pt; 
          margin-bottom: 20pt;
        }
        .analytics-summary {
          background: #f8fafc;
          padding: 12pt;
          border: 1px solid #e2e8f0;
          margin: 20pt 0;
          page-break-inside: avoid;
        }
        .metadata-table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 20pt;
          font-size: 10pt;
        }
        .metadata-table td {
          border: 1px solid #ddd;
          padding: 6pt;
          vertical-align: top;
        }
        .page-break { page-break-before: always; }
        @media print {
          .no-print { display: none; }
        }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>Enterprise Content Analysis Report</h1>
        <p><strong>Generation ID:</strong> ${exportPackage.metadata.generation_id || 'N/A'}</p>
        <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
        <p><strong>Model:</strong> ${exportPackage.metadata.model_used || 'N/A'}</p>
      </div>

      <div class="analytics-summary">
        <h2>Performance Analytics</h2>
        <table class="metadata-table">
          <tr>
            <td><strong>SEO Score</strong></td>
            <td>${exportPackage.metadata.content_analytics?.seo_optimization?.score || 'N/A'}</td>
            <td><strong>Engagement Score</strong></td>
            <td>${exportPackage.metadata.content_analytics?.engagement_prediction?.score || 'N/A'}</td>
          </tr>
          <tr>
            <td><strong>Readability</strong></td>
            <td>${exportPackage.metadata.content_analytics?.readability_score || 'N/A'}</td>
            <td><strong>Monetization Potential</strong></td>
            <td>${exportPackage.metadata.cost_analysis?.monetization_potential || 'N/A'}</td>
          </tr>
        </table>
      </div>

      <div class="page-break"></div>
      
      <h2>Generated Content</h2>
      ${convertToHTML(content)}
      
      <div class="page-break"></div>
      
      <h2>Technical Metadata</h2>
      <table class="metadata-table">
        <tr>
          <td><strong>Tokens Consumed</strong></td>
          <td>${exportPackage.metadata.tokens_consumed || 'N/A'}</td>
        </tr>
        <tr>
          <td><strong>Generation Time</strong></td>
          <td>${exportPackage.metadata.generation_time || 'N/A'}ms</td>
        </tr>
        <tr>
          <td><strong>Cost Analysis</strong></td>
          <td>${exportPackage.metadata.cost_analysis?.generation_cost || 'N/A'}</td>
        </tr>
        <tr>
          <td><strong>Projected ROI</strong></td>
          <td>${exportPackage.metadata.cost_analysis?.projected_roi || 'N/A'}x</td>
        </tr>
      </table>

      <div class="no-print" style="position: fixed; top: 20px; right: 20px;">
        <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
          Print to PDF
        </button>
      </div>
    </body>
    </html>
  `;
}

function createEnterprisePreview(previewData: any): string {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Enterprise Content Preview</title>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          min-height: 100vh;
          padding: 20px;
        }
        .container {
          max-width: 1200px;
          margin: 0 auto;
          background: white;
          border-radius: 20px;
          box-shadow: 0 20px 40px rgba(0,0,0,0.1);
          overflow: hidden;
        }
        .header {
          background: linear-gradient(135deg, #2563eb, #1d4ed8);
          color: white;
          padding: 30px;
          position: relative;
          overflow: hidden;
        }
        .header::before {
          content: '';
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
          animation: float 20s infinite linear;
        }
        @keyframes float {
          0% { transform: translateX(-50px) translateY(-50px); }
          100% { transform: translateX(-100px) translateY(-100px); }
        }
        .header-content { position: relative; z-index: 1; }
        .title { font-size: 2.5rem; font-weight: 700; margin-bottom: 10px; }
        .subtitle { font-size: 1.2rem; opacity: 0.9; }
        .dashboard {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 20px;
          padding: 30px;
          background: #f8fafc;
        }
        .metric-card {
          background: white;
          padding: 25px;
          border-radius: 15px;
          text-align: center;
          box-shadow: 0 5px 15px rgba(0,0,0,0.08);
          border: 1px solid #e2e8f0;
          transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .metric-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        .metric-value {
          font-size: 2.5rem;
          font-weight: 700;
          margin-bottom: 8px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .metric-label {
          color: #64748b;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          font-size: 0.875rem;
        }
        .content-section {
          padding: 40px;
          line-height: 1.8;
          font-size: 1.1rem;
          color: #374151;
        }
        .competitive-intelligence {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          color: white;
          padding: 30px;
          margin: 30px;
          border-radius: 15px;
          box-shadow: 0 10px 25px rgba(240, 147, 251, 0.3);
        }
        .ci-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }
        .ci-metric {
          background: rgba(255,255,255,0.2);
          padding: 20px;
          border-radius: 10px;
          text-align: center;
          backdrop-filter: blur(10px);
        }
        .ci-value {
          font-size: 2rem;
          font-weight: 700;
          margin-bottom: 5px;
        }
        .print-controls {
          position: fixed;
          top: 20px;
          right: 20px;
          display: flex;
          gap: 10px;
          z-index: 1000;
        }
        .btn {
          background: #2563eb;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 500;
          transition: background 0.3s ease;
        }
        .btn:hover { background: #1d4ed8; }
        .btn-secondary {
          background: #64748b;
        }
        .btn-secondary:hover { background: #475569; }
        @media print {
          .print-controls { display: none; }
          body { background: white; padding: 0; }
          .container { box-shadow: none; }
        }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      </style>
    </head>
    <body>
      <div class="print-controls">
        <button class="btn" onclick="window.print()">Print Report</button>
        <button class="btn btn-secondary" onclick="window.close()">Close</button>
      </div>

      <div class="container">
        <div class="header">
          <div class="header-content">
            <h1 class="title">Enterprise Content Analysis</h1>
            <p class="subtitle">AI-Powered Performance Intelligence Report</p>
          </div>
        </div>

        <div class="dashboard">
          <div class="metric-card">
            <div class="metric-value">${previewData.analytics?.seo_optimization?.score || 0}</div>
            <div class="metric-label">SEO Optimization</div>
          </div>
          <div class="metric-card">
            <div class="metric-value">${previewData.analytics?.engagement_prediction?.score || 0}</div>
            <div class="metric-label">Engagement Score</div>
          </div>
          <div class="metric-card">
            <div class="metric-value">${previewData.analytics?.readability_score || 0}</div>
            <div class="metric-label">Readability Index</div>
          </div>
        </div>

        ${previewData.competitive_intelligence ? `
        <div class="competitive-intelligence">
          <h2 style="margin-bottom: 20px; font-size: 1.8rem;">🎯 Competitive Intelligence</h2>
          <div class="ci-grid">
            <div class="ci-metric">
              <div class="ci-value">${previewData.competitive_intelligence.market_position}%</div>
              <div>Market Position</div>
            </div>
            <div class="ci-metric">
              <div class="ci-value">${previewData.competitive_intelligence.innovation_score}/100</div>
              <div>Innovation Score</div>
            </div>
            <div class="ci-metric">
              <div class="ci-value pulse">${previewData.competitive_intelligence.monetization_potential}</div>
              <div>Revenue Potential</div>
            </div>
          </div>
        </div>
        ` : ''}

        <div class="content-section">
          <h2 style="color: #1f2937; margin-bottom: 30px; font-size: 2rem;">Generated Content</h2>
          ${convertToHTML(previewData.content)}
        </div>

        ${previewData.metadata ? `
        <div style="background: #f8fafc; padding: 30px; margin: 30px; border-radius: 15px; border-left: 5px solid #2563eb;">
          <h3 style="color: #1f2937; margin-bottom: 20px;">Generation Metadata</h3>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; font-size: 0.95rem;">
            <div><strong>Model Used:</strong> ${previewData.metadata.model_used || 'N/A'}</div>
            <div><strong>Tokens Consumed:</strong> ${previewData.metadata.tokens_consumed || 'N/A'}</div>
            <div><strong>Generation Time:</strong> ${previewData.metadata.generation_time || 'N/A'}ms</div>
            <div><strong>Cost:</strong> ${previewData.metadata.cost_analysis?.generation_cost || 'N/A'}</div>
            <div><strong>Projected ROI:</strong> ${previewData.metadata.cost_analysis?.projected_roi || 'N/A'}x</div>
            <div><strong>Quality Score:</strong> ${previewData.metadata.quality_metrics?.coherence_score || 'N/A'}/100</div>
          </div>
        </div>
        ` : ''}
      </div>

      <script>
        // Add some interactive elements
        document.addEventListener('DOMContentLoaded', function() {
          // Animate metric cards on load
          const cards = document.querySelectorAll('.metric-card');
          cards.forEach((card, index) => {
            setTimeout(() => {
              card.style.transform = 'translateY(-5px)';
              card.style.boxShadow = '0 10px 25px rgba(0,0,0,0.15)';
            }, index * 200);
          });
          
          // Add click handler for metric cards
          cards.forEach(card => {
            card.addEventListener('click', function() {
              this.style.transform = 'scale(1.05)';
              setTimeout(() => {
                this.style.transform = 'translateY(-5px)';
              }, 200);
            });
          });
        });
      </script>
    </body>
    </html>
  `;
}

export default GeneratedContentDisplay;