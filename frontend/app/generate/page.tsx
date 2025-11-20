// File: frontend/app/generate/page.tsx
// Enterprise content generation with drill-down template-style selection
// Main generation interface with unified template-style selection flow
// RELEVANT FILES: components/TemplateStyleDrillDown.tsx, hooks/useTemplateStyleDrillDown.ts, lib/template-style-mapping.ts

"use client";
import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form } from "@/components/ui/form";
import { SubmitHandler } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { useEnhancedGeneration } from "@/hooks/useEnhancedGeneration";
import { useSettings } from '@/lib/settings-context'
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { 
  Check, 
  Copy, 
  Download, 
//  Save,
  Eye, 
  FileText, 
  Loader2, 
  Zap, 
  AlertCircle,
  Settings,
  ArrowLeft
} from "lucide-react";

import DynamicParameters from "@/components/DynamicParameters";
import { useQueryClient } from "@tanstack/react-query";
import GeneratingDialog from "@/components/GeneratingDialog";
import { useTemplates } from "@/hooks/useTemplates";
import { useStyleProfiles } from "@/hooks/useStyleProfiles";
import TemplateStyleDrillDown from '@/components/TemplateStyleDrillDown';
import { z } from "zod";

// Schema Definition
const generateContentSchema = z.object({
  templateId: z.string().min(1),
  styleProfileId: z.string().min(1),
  dynamic_parameters: z.record(z.union([z.string(), z.number(), z.boolean()])),
  platform: z.string(),
});

type GenerateContentFormValues = z.infer<typeof generateContentSchema>;

interface StyleProfile {
  id: string;
  name: string;
  description?: string;
  category?: string;
  tone?: string;
}

interface ExtendedStyleProfile {
  id: string;
  name: string;
  description?: string;
  category?: string;
  tone?: string;
  voice?: string;
  structure?: string;
  system_prompt?: string;
  settings?: Record<string, unknown>;
  filename?: string;
}

interface Template {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty?: string;
  estimatedLength?: string;
  icon?: string;
  templateData?: {
    template_type?: string;
    parameters?: Record<string, unknown>;
    sections?: unknown[];
    instructions?: string;
    content_format?: string;
    output_structure?: string;
    section_order?: string[];
    validation_rules?: string[];
    tone?: Record<string, unknown>;
    generation_mode?: string;
  };
}

// Environment configuration
const USE_BACKEND_API = process.env.NEXT_PUBLIC_USE_BACKEND_API === 'true';

// Enhanced Generation Preview Component (unchanged)
const EnhancedGenerationPreview = ({ 
  isGenerating, 
  generatedContent, 
  onCancel, 
  onSave, 
  templateName, 
  styleProfile 
}: {
  isGenerating: boolean;
  generatedContent?: string;
  onCancel: () => void;
  onSave: () => void;
  templateName?: string;
  styleProfile?: string;
}) => {
  const [isPreview, setIsPreview] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopy = async () => {
    if (!generatedContent) return;
    
    try {
      await navigator.clipboard.writeText(generatedContent);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleExport = (format: 'markdown' | 'html' | 'pdf') => {
    if (!generatedContent) return;

    let exportContent = generatedContent;
    let fileName = `generated-content-${new Date().toISOString().split('T')[0]}.${format}`;
    let mimeType = 'text/plain';

    switch (format) {
      case 'html':
        exportContent = `<!DOCTYPE html>
<html>
<head>
  <title>Generated Content</title>
  <meta charset="UTF-8">
  <style>
    body { 
      font-family: Georgia, 'Times New Roman', serif;
      max-width: 800px; 
      margin: 0 auto; 
      padding: 3rem 2rem; 
      line-height: 1.8; 
      color: #2d3748;
      background: #ffffff;
    }
    h1 { 
      color: #1a202c; 
      font-size: 2.5rem; 
      margin-bottom: 1.5rem; 
      border-bottom: 3px solid #667eea;
      padding-bottom: 0.5rem;
    }
    h2 { 
      color: #2d3748; 
      font-size: 1.875rem; 
      margin-top: 2.5rem; 
      margin-bottom: 1rem;
    }
    h3 { 
      color: #4a5568; 
      font-size: 1.5rem; 
      margin-top: 2rem; 
      margin-bottom: 0.75rem;
    }
    p { 
      margin-bottom: 1.25rem; 
      text-align: justify;
      text-indent: 1.5rem;
    }
    strong { color: #1a202c; }
    em { color: #4a5568; }
    blockquote {
      border-left: 4px solid #667eea;
      padding-left: 1.5rem;
      margin: 1.5rem 0;
      font-style: italic;
      color: #4a5568;
    }
    .metadata {
      background: #f7fafc;
      padding: 1.5rem;
      border-radius: 8px;
      margin: 2rem 0;
      border: 1px solid #e2e8f0;
    }
    .export-note {
      font-size: 0.875rem;
      color: #718096;
      text-align: center;
      margin-top: 3rem;
      padding-top: 1rem;
      border-top: 1px solid #e2e8f0;
    }
  </style>
</head>
<body>
  <div class="metadata">
    <strong>Generated with:</strong> ${templateName || 'Unknown Template'}<br>
    <strong>Style:</strong> ${styleProfile || 'Default'}<br>
    <strong>Generated:</strong> ${new Date().toLocaleString()}
  </div>
  
  ${convertMarkdownToHTML(generatedContent)}
  
  <div class="export-note">
    Generated by WriterzRoom • ${new Date().toLocaleDateString()}
  </div>
</body>
</html>`;
        mimeType = 'text/html';
        break;
        
      case 'pdf':
        // For PDF, create print-optimized HTML
        exportContent = createPrintOptimizedHTML(generatedContent, templateName, styleProfile);
        fileName = fileName.replace('.pdf', '.html');
        mimeType = 'text/html';
        break;
        
      default:
        // Markdown format
        exportContent = `# Generated Content

**Template:** ${templateName || 'Unknown'}  
**Style:** ${styleProfile || 'Default'}  
**Generated:** ${new Date().toLocaleString()}

---

${generatedContent}

---
*Generated by WriterzRoom*`;
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

  if (isGenerating) {
    return (
      <Card className="bg-white/10 backdrop-blur-sm border-white/20">
        <CardContent className="p-8 text-center">
          <Loader2 className="h-12 w-12 animate-spin text-purple-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Generating Content...</h3>
          <p className="text-gray-300">Please wait while our AI creates your content</p>
          <Button 
            variant="outline" 
            onClick={onCancel}
            className="mt-4 border-white/20 text-white hover:bg-white/10"
          >
            Cancel
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!generatedContent) {
    return null;
  }

  return (
    <Card className="bg-white/10 backdrop-blur-sm border-white/20">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-white flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Generated Content
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsPreview(!isPreview)}
              className="border-white/20 text-white hover:bg-white/10"
            >
              <Eye className="h-4 w-4 mr-1" />
              {isPreview ? 'Raw' : 'Preview'}
            </Button>
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
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Content Stats */}
        <div className="flex items-center gap-4 mb-4 text-sm text-gray-300">
          <span>{generatedContent.split(/\s+/).length} words</span>
          <span>{generatedContent.length} characters</span>
          <span>{Math.ceil(generatedContent.split(/\s+/).length / 200)} min read</span>
        </div>

        {/* Content Display */}
        <div className="mb-6">
          {isPreview ? (
            <div className="bg-white rounded-lg p-6 shadow-inner">
              <div 
                className="prose prose-lg max-w-none text-gray-800"
                style={{
                  fontFamily: 'Georgia, "Times New Roman", serif',
                  lineHeight: '1.8',
                  fontSize: '1.1rem'
                }}
                dangerouslySetInnerHTML={{ 
                  __html: convertMarkdownToHTML(generatedContent) 
                }}
              />
            </div>
          ) : (
            <div className="bg-gray-900 rounded-lg p-4 border border-gray-700">
              <pre className="text-gray-200 whitespace-pre-wrap font-mono text-sm overflow-x-auto">
                {generatedContent}
              </pre>
            </div>
          )}
        </div>

        {/* Export Options */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-white/20">
          <div className="flex flex-wrap gap-2">
            <Button
              onClick={() => handleExport('markdown')}
              variant="outline"
              size="sm"
              className="border-white/20 text-white hover:bg-white/10"
            >
              <Download className="h-4 w-4 mr-1" />
              Markdown
            </Button>
            <Button
              onClick={() => handleExport('html')}
              variant="outline"
              size="sm"
              className="border-white/20 text-white hover:bg-white/10"
            >
              <Download className="h-4 w-4 mr-1" />
              HTML
            </Button>
            <Button
              onClick={() => handleExport('pdf')}
              variant="outline"
              size="sm"
              className="border-white/20 text-white hover:bg-white/10"
            >
              <Download className="h-4 w-4 mr-1" />
              PDF Ready
            </Button>
          </div>
          
          <Button
            onClick={onSave}
            className="bg-linear-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
          >
            <FileText className="h-4 w-4 mr-2" />
            View in Content
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Helper function to convert markdown-like content to HTML
function convertMarkdownToHTML(content: string): string {
  return content
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(?!<[uo]l>|<h[1-6]>)(.+)$/gm, '<p>$1</p>')
    .replace(/<\/p><p><ul>/g, '</p><ul>')
    .replace(/<\/ul><p>/g, '</ul><p>');
}

// Helper function to create print-optimized HTML for PDF
function createPrintOptimizedHTML(content: string, templateName?: string, styleProfile?: string): string {
  return `<!DOCTYPE html>
<html>
<head>
  <title>Generated Content - Print Version</title>
  <meta charset="UTF-8">
  <style>
    @page { 
      margin: 1in; 
      size: A4;
    }
    body { 
      font-family: 'Times New Roman', serif;
      font-size: 12pt;
      line-height: 1.6;
      color: #000;
      background: #fff;
    }
    h1 { 
      font-size: 18pt; 
      margin-bottom: 12pt; 
      page-break-after: avoid;
    }
    h2 { 
      font-size: 16pt; 
      margin-top: 18pt; 
      margin-bottom: 10pt; 
      page-break-after: avoid;
    }
    h3 { 
      font-size: 14pt; 
      margin-top: 14pt; 
      margin-bottom: 8pt; 
      page-break-after: avoid;
    }
    p { 
      margin-bottom: 8pt; 
      text-align: justify;
    }
    .header {
      border-bottom: 1pt solid #000;
      padding-bottom: 8pt;
      margin-bottom: 16pt;
    }
    .footer {
      margin-top: 24pt;
      padding-top: 8pt;
      border-top: 1pt solid #000;
      font-size: 10pt;
      text-align: center;
    }
    @media print {
      body { margin: 0; }
      .no-print { display: none; }
    }
  </style>
</head>
<body>
  <div class="header">
    <strong>Template:</strong> ${templateName || 'Unknown'}<br>
    <strong>Style:</strong> ${styleProfile || 'Default'}<br>
    <strong>Generated:</strong> ${new Date().toLocaleString()}
  </div>
  
  ${convertMarkdownToHTML(content)}
  
  <div class="footer">
    Generated by WriterzRoom • ${new Date().toLocaleDateString()}
  </div>
  
  <div class="no-print" style="position: fixed; top: 20px; right: 20px;">
    <button onclick="window.print()" style="background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
      Print to PDF
    </button>
  </div>
</body>
</html>`;
}
// Main Component
export default function GeneratePage() {
  const router = useRouter();
  const [isGeneratingDialogOpen, setIsGeneratingDialogOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState<'selection' | 'generation'>('selection');
 // const [savedContentId, setSavedContentId] = useState<string | null>(null);
 // const [savedContentId, setSavedContentId] = useState<string | null>(null);
  // Store selected template/style separately to avoid re-render loops
  const [finalSelections, setFinalSelections] = useState<{
    template: Template | null;
    style: ExtendedStyleProfile | null;
  }>({ template: null, style: null });
  
  const { data: styleProfiles, isLoading: profilesLoading, isError: profilesError } = useStyleProfiles();
  const { data: templates, isLoading: templatesLoading, isError: templatesError, error: templatesErrorDetails } = useTemplates();

  const {
    isGenerating,
    result,
    error,
    startGeneration,
    cancelGeneration,
    resetGeneration,
  } = useEnhancedGeneration();

  
  const convertedTemplates = useMemo(() => 
    (templates || []).map(template => ({
      id: template.id,
      title: template.title,
      description: template.description || '',
      category: template.category || 'General',
      difficulty: template.difficulty,
      estimatedLength: template.estimatedLength,
      icon: template.icon,
      templateData: template.templateData
    })), [templates]);

  const convertedStyleProfiles = useMemo(() => 
    (styleProfiles || []).map(profile => ({
      id: profile.id,
      name: profile.name,
      description: profile.description || '',
      category: profile.category || 'General',
      tone: profile.tone
    })), [styleProfiles]);

  const form = useForm<GenerateContentFormValues>({
    resolver: zodResolver(generateContentSchema),
    defaultValues: {
      templateId: "",
      styleProfileId: "",
      dynamic_parameters: {},
      platform: "web",
    },
    mode: "onChange",
  });

  const watchedTemplateId = form.watch("templateId");
  const watchedStyleProfileId = form.watch("styleProfileId");

  // Use finalSelections for actual template/style data when in generation step
  const selectedTemplate = currentStep === 'generation' 
    ? finalSelections.template 
    : convertedTemplates.find(t => t.id === watchedTemplateId) || null;
    
  const selectedStyleProfile = currentStep === 'generation'
    ? finalSelections.style
    : styleProfiles?.find(sp => sp.id === watchedStyleProfileId) || null;

  const queryClient = useQueryClient();
  const { generationSettings } = useSettings();

  useEffect(() => {
    const handleSettingsUpdate = (e: CustomEvent) => {
      console.log('Generation settings updated:', e.detail.generationSettings)
      queryClient.invalidateQueries({ queryKey: ['generation-settings'] })
    }
  
    window.addEventListener('generation-settings-updated', handleSettingsUpdate as EventListener)
    return () => window.removeEventListener('generation-settings-updated', handleSettingsUpdate as EventListener)
  }, [queryClient])

  // Force fresh data on page load to fix caching issues
  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ['templates'] });
    queryClient.invalidateQueries({ queryKey: ['style-profiles'] });
  }, [queryClient]);

  // Handle URL parameters for template pre-selection
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const templateParam = urlParams.get('template');
    
    if (templateParam && templates?.find(t => t.id === templateParam)) {
      form.setValue('templateId', templateParam);
      console.log('Template pre-selected from URL:', templateParam);
    }
  }, [templates, form]);

  // Auto-save functionality
  const autoSaveToGeneratedContentFolder = useCallback(async () => {
    if (!result?.content) return;

    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
      const templateSlug = selectedTemplate?.id || 'content';
      const filename = `${templateSlug}_${timestamp}_${Date.now()}`;
    
    const response = await fetch('/api/content', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: filename,
        content: result.content,
        metadata: {
        template: selectedTemplate?.id,
        style_profile: selectedStyleProfile?.id,
        word_count: result.content.split(' ').length,
        created_at: new Date().toISOString(),
        preview: result.content.split('\n').find(line => line.trim().length > 0)?.replace(/^#+\s*/, '').trim().substring(0, 100),
      },
        status: 'completed',
        type: 'article',
      }),
    });
  
    if (!response.ok) {
      throw new Error(`Save failed: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ Auto-saved content:', data);

  } catch (error) {
    console.error('❌ Auto-save failed:', error);
  }
}, [result?.content, selectedTemplate?.id, selectedStyleProfile?.id]);

  useEffect(() => {
    if (result?.content && generationSettings.autoSave && !isGenerating) {
      const saveTimeout = setTimeout(() => {
        autoSaveToGeneratedContentFolder();
      }, 2000);

      return () => clearTimeout(saveTimeout);
    }
  }, [result?.content, isGenerating, generationSettings.autoSave, autoSaveToGeneratedContentFolder]);

  useEffect(() => {
    if (currentStep !== 'generation' || !selectedTemplate?.templateData?.parameters) {
      return;
    }

    try {
      const newDefaults: Record<string, string | number | boolean> = {};

      Object.entries(selectedTemplate.templateData.parameters).forEach(([paramName, param]) => {
        if (!param || typeof param !== 'object' || !paramName) {
          console.warn('Invalid enhanced parameter:', param);
          return;
        }

        const typedParam = param as { default?: unknown; type?: string; [key: string]: unknown };
        
        if (
          typeof typedParam.default === "string" ||
          typeof typedParam.default === "number" ||
          typeof typedParam.default === "boolean"
        ) {
          newDefaults[paramName] = typedParam.default;
        } else if (Array.isArray(typedParam.default) && typedParam.default.length > 0 && typeof typedParam.default[0] === "string") {
          newDefaults[paramName] = typedParam.default[0];
        } else {
          switch (typedParam.type) {
            case "text":
            case "textarea":
            case "select":
              newDefaults[paramName] = "";
              break;
            case "number":
            case "range":
              newDefaults[paramName] = 0;
              break;
            case "checkbox":
              newDefaults[paramName] = false;
              break;
            case "date":
              newDefaults[paramName] = "";
              break;
            default:
              newDefaults[paramName] = "";
          }
        }
      });

      console.log('🔧 Setting enhanced template defaults:', newDefaults);
      form.setValue("dynamic_parameters", newDefaults);

    } catch (error) {
      console.error('Error processing enhanced template parameters:', error);
    }
  }, [currentStep, selectedTemplate, form]);
  
  useEffect(() => {
    setIsGeneratingDialogOpen(isGenerating);
  }, [isGenerating]);

  // Handle drill-down completion
  const handleDrillDownComplete = async (template: Template, style: StyleProfile) => {
    console.log('🔄 Fetching full template details for:', template.id);
    
    try {
      const response = await fetch(`/api/templates/${template.id}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch template details: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data.success || !data.data) {
        throw new Error('Invalid template response format');
      }
      
      console.log('✅ Fetched template details:', {
        id: data.data.id,
        parametersCount: Object.keys(data.data.parameters || {}).length
      });
      
      const enrichedTemplate = {
        ...template,
        templateData: {
          ...template.templateData,
          parameters: data.data.parameters
        }
      };
      
      setFinalSelections({
        template: enrichedTemplate,
        style: style as ExtendedStyleProfile
      });
      
      form.setValue('templateId', template.id, { shouldValidate: true });
      form.setValue('styleProfileId', style.id, { shouldValidate: true });
      
      setCurrentStep('generation');
      
    } catch (error) {
      console.error('❌ Failed to fetch template details:', error);
      setFinalSelections({
        template,
        style: style as ExtendedStyleProfile
      });
      form.setValue('templateId', template.id, { shouldValidate: true });
      form.setValue('styleProfileId', style.id, { shouldValidate: true });
      
      setCurrentStep('generation');
    }
  };
  // Handle drill-down template selection
  const handleDrillDownTemplateSelect = (template: Template) => {
    // Just track in form for drill-down component
    form.setValue('templateId', template.id);
  };

  // Handle drill-down style selection  
  const handleDrillDownStyleSelect = (style: StyleProfile | null) => {
    if (style) {
      form.setValue('styleProfileId', style.id);
    }
  };


// Get enhanced parameters for display
  const enhancedParameters = useMemo(() => {
    const template = currentStep === 'generation' ? finalSelections.template : selectedTemplate;
    if (!template || !template.templateData?.parameters) {
      return [];
    }
    
    return Object.entries(template.templateData.parameters).map(([key, param]) => {
      
      const typedParam = param as { 
        label?: string;
        type?: "text" | "textarea" | "select" | "number" | "checkbox" | "multiselect" | "range" | "date";
        options?: Record<string, string> | string[];
        default?: string | number | boolean;
        required?: boolean;
        placeholder?: string;
        description?: string;
        commonly_used?: boolean;
        affects_approach?: boolean;
        affects_scope?: boolean;
        affects_tone?: boolean;
        validation?: {
          min?: number;
          max?: number;
          pattern?: string;
          message?: string;
        };
      };
      
      return {
        name: key,
        label: typedParam.label || key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        type: typedParam.type || 'text' as const,
        options: typedParam.options,
        default: typedParam.default,
        required: typedParam.required || false,
        placeholder: typedParam.placeholder,
        description: typedParam.description,
        commonly_used: typedParam.commonly_used || false,
        affects_approach: typedParam.affects_approach || false,
        affects_scope: typedParam.affects_scope || false,
        affects_tone: typedParam.affects_tone || false,
        validation: typedParam.validation,
      };
    });
  }, [selectedTemplate, currentStep, finalSelections.template]);

  // Validate required fields before allowing generation
  const dynamicParams = form.watch("dynamic_parameters");
  const canGenerate = useMemo(() => {
    // In generation step, use finalSelections which are guaranteed to be set
    if (currentStep === 'generation') {
      if (!finalSelections.template || !finalSelections.style || isGenerating) {
        return false;
      }
      
      // Check required parameters using finalSelections
      const requiredParams = enhancedParameters.filter(p => p.required);
      if (requiredParams.length === 0) return true;

      return requiredParams.every(param => {
        const value = dynamicParams?.[param.name];
        if (value === undefined || value === null || value === '') return false;
        if (typeof value === 'string' && value.trim() === '') return false;
        return true;
      });
    }
    
    // In selection step, use form values
    if (!watchedTemplateId || !watchedStyleProfileId || isGenerating || templatesLoading || profilesLoading) {
      return false;
    }

    const requiredParams = enhancedParameters.filter(p => p.required);
    if (requiredParams.length === 0) return true;

    return requiredParams.every(param => {
      const value = dynamicParams?.[param.name];
      if (value === undefined || value === null || value === '') return false;
      if (typeof value === 'string' && value.trim() === '') return false;
      return true;
    });
  }, [currentStep, finalSelections, watchedTemplateId, watchedStyleProfileId, isGenerating, templatesLoading, profilesLoading, dynamicParams, enhancedParameters]);


  if (templatesLoading || profilesLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading enhanced templates and style profiles...</p>
        </div>
      </div>
    );
  }

  if (templatesError || profilesError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Card className="bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800 max-w-md">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 text-red-700 dark:text-red-300">
                <AlertCircle className="h-5 w-5" />
                <div>
                  <h3 className="font-medium">Error Loading Data</h3>
                  <p className="text-sm mt-1">
                    {templatesError && "Failed to load enhanced templates. "}
                    {profilesError && "Failed to load style profiles."}
                  </p>
                  {templatesErrorDetails?.message && (
                    <p className="text-xs text-gray-500 mt-2">
                      {templatesErrorDetails.message}
                    </p>
                  )}
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

  if (!templates || !Array.isArray(templates) || templates.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Card className="bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800 max-w-md">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3 text-yellow-700 dark:text-yellow-300">
                <AlertCircle className="h-5 w-5" />
                <div>
                  <h3 className="font-medium">No Enhanced Templates Available</h3>
                  <p className="text-sm mt-1">
                    No templates found. Please check your backend connection.
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    Templates: {templates?.length || 0} | Backend: {USE_BACKEND_API ? 'Enabled' : 'Disabled'}
                  </p>
                </div>
              </div>
              <Button 
                variant="outline" 
                className="mt-4 w-full" 
                onClick={() => window.location.reload()}
              >
                Refresh
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Enhanced form submission handler
  const onSubmit: SubmitHandler<GenerateContentFormValues> = async (values) => {
    console.log('🚀 Enhanced form submitted with values:', values);
    console.log('📊 Enhanced dynamic parameters:', values.dynamic_parameters);
    console.log('📋 Selected enhanced template:', selectedTemplate?.templateData?.template_type);

    const params = values.dynamic_parameters || {};
    console.log('⚙️ Using generation settings:', generationSettings);
    console.log('📊 Raw enhanced form parameters:', params);
    console.log('✅ Starting enhanced generation with all parameters...');

    type GenerationMode = "standard" | "premium" | "enterprise" | undefined;
    const generationMode: GenerationMode = 
      selectedTemplate?.templateData?.generation_mode === "standard" ||
      selectedTemplate?.templateData?.generation_mode === "premium" ||
      selectedTemplate?.templateData?.generation_mode === "enterprise"
        ? selectedTemplate.templateData.generation_mode
        : "standard";

    const enhancedParametersWithSettings = {
      ...params,
      preferred_length: getLengthFromTokens(generationSettings.maxTokens),
      creativity_level: getCreativityLevel(generationSettings.temperature),
      content_quality: generationSettings.contentQuality,
    };

    const enhancedRequest = {
      template: values.templateId,
      style_profile: values.styleProfileId,
      dynamic_parameters: enhancedParametersWithSettings,
      platform: values.platform,
      priority: generationSettings.contentQuality === 'premium' ? 5 : 
               generationSettings.contentQuality === 'balanced' ? 3 : 1,
      timeout_seconds: generationSettings.contentQuality === 'premium' ? 600 : 300,
      generation_mode: generationMode,

      generation_settings: {
        max_tokens: generationSettings.maxTokens,
        temperature: generationSettings.temperature,
        quality_mode: generationSettings.contentQuality,
        auto_save: generationSettings.autoSave,
      },

      template_config: selectedTemplate?.templateData ? {
        template_type: selectedTemplate.templateData.template_type,
        content_format: selectedTemplate.templateData.content_format,
        output_structure: selectedTemplate.templateData.output_structure,
        section_order: selectedTemplate.templateData.section_order,
        validation_rules: selectedTemplate.templateData.validation_rules,
        tone: selectedTemplate.templateData.tone,
        instructions: selectedTemplate.templateData.instructions,
      } : undefined,
    };

    console.log('🚀 Enhanced generation request with user settings:', enhancedRequest);
    startGeneration(enhancedRequest);
    setCurrentStep('generation'); 
  };

  const getLengthFromTokens = (tokens: number): string => {
    if (tokens <= 1000) return 'short'
    if (tokens <= 2000) return 'medium' 
    if (tokens <= 4000) return 'long'
    return 'comprehensive'
  }

  const getCreativityLevel = (temperature: number): string => {
    if (temperature <= 0.3) return 'focused'
    if (temperature <= 0.7) return 'balanced'
    return 'creative'
  }


//   const handleSaveContent = async () => {
//    console.log('🔍 Current savedContentId:', savedContentId);
//    
//    // If already saved, redirect
//    if (savedContentId) {
//      window.location.href = `/content/${savedContentId}`;
//      return;
//    }
//
//    // Otherwise, save now
//    if (!result?.content) {
//      window.location.href = '/content';
//      return;
//    }
//
//    try {
//      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
//      const templateSlug = selectedTemplate?.id || 'content';
//      const filename = `${templateSlug}_${timestamp}_${Date.now()}`;
//    
//      const response = await fetch('/api/content', {
//        method: 'POST',
//        headers: { 'Content-Type': 'application/json' },
//        body: JSON.stringify({
//          title: filename,
//          content: result.content,
//          metadata: {
//            template: selectedTemplate?.id,
//            style_profile: selectedStyleProfile?.id,
//            word_count: result.content.split(' ').length,
//            created_at: new Date().toISOString(),
//          },
//          status: 'completed',
//          type: 'article',
//        }),
//      });
//    
//      if (!response.ok) throw new Error(`Save failed: ${response.status}`);
//    
//      const data = await response.json();
//      console.log('✅ Manual save:', data);
//      window.location.href = `/content/${data.contentId}`;
//      
//  } catch (error) {
//    console.error('❌ Save failed:', error);
//    window.location.href = '/content';
//  }
//};
    const handleViewContent = () => {
      router.push('/content');
    };

  return (
    <div className="max-w-6xl mx-auto space-y-8 text-gray-900 dark:text-white">
      {/* Enhanced Header */}
      <div className="text-center space-y-4">
      
        <h1 className="text-5xl font-bold bg-linear-to-r from-purple-400 via-pink-500 to-purple-600 bg-clip-text text-transparent">

          Generate Enhanced AI Content
        </h1>
        <p className="text-lg text-gray-300 max-w-2xl mx-auto">
          Create high-quality content using our advanced AI models with enhanced dynamic templates. 
          Select a template and style profile to get started.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {currentStep === 'selection' ? (
            <TemplateStyleDrillDown
              templates={convertedTemplates}
              styleProfiles={convertedStyleProfiles}
              selectedTemplate={selectedTemplate}
              selectedStyle={convertedStyleProfiles.find(sp => sp.id === watchedStyleProfileId) || null}
              styleProfileSectionId="style-profile-section"
              onTemplateSelect={handleDrillDownTemplateSelect}
              onStyleSelect={handleDrillDownStyleSelect}
              onProceed={() => {
                const template = convertedTemplates.find(t => t.id === watchedTemplateId);
                const style = convertedStyleProfiles.find(sp => sp.id === watchedStyleProfileId);
                if (template && style) {
                  handleDrillDownComplete(template, style);
                }
              }}
            />
          ) : (
            <>
              {/* Back Button */}
              <div className="mb-6">
                <Button
                  variant="outline"
                  onClick={() => setCurrentStep('selection')}
                  className="flex items-center gap-2"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back to Template Selection
                </Button>
              </div>

              {/* Selection Summary */}
              <Card className="bg-linear-to-r from-purple-900/30 to-pink-900/30 border-purple-500/40 mb-6">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-white mb-1 bg-linear-to-r from-purple-600/30 to-pink-600/30 px-4 py-2 rounded-lg border border-purple-500/50 inline-block">Ready to Generate</h3>
                      <p className="text-sm text-gray-300">
                        Template: <span className="font-medium">{selectedTemplate?.title}</span>
                        {' • '}
                        Style: <span className="font-medium">{selectedStyleProfile?.name}</span>
                      </p>
                    </div>
                    <Badge variant="outline" className="bg-green-500/20 text-green-300 border-green-500/50">
                      Optimized Pairing
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              
              {/* Enhanced Dynamic Parameters */}
              {selectedTemplate && enhancedParameters.length > 0 && (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="flex items-center gap-2 text-white">
                          <div className="p-2 bg-linear-to-r from-purple-500 to-pink-500 rounded-lg">
                            <Settings className="h-5 w-5 text-white" />
                          </div>
                          Template Parameters
                        </CardTitle>
                        <CardDescription className="text-gray-200">
                          Configure your {selectedTemplate.templateData?.template_type || 'dynamic'} template 
                          with {enhancedParameters.length} specialized parameters.
                        </CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        {selectedTemplate.templateData?.template_type && (
                          <Badge variant="secondary">
                            {selectedTemplate.templateData.template_type}
                          </Badge>
                        )}
                        <Badge variant="outline">
                          {enhancedParameters.length} params
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <DynamicParameters parameters={enhancedParameters} />
                  </CardContent>
                </Card>
              )}

              {/* Enhanced Generation Button */}
              <Card className="border-2 border-purple-500/30 bg-purple-950/20">
                <CardContent className="pt-6">
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-3">
                      <div className="p-3 bg-linear-to-r from-purple-500 to-pink-500 rounded-lg">
                        <Zap className="h-6 w-6 text-purple-300" />
                      </div>
                      <div>
                        <h3 className="font-semibold bg-linear-to-r from-purple-500/20 to-pink-500/20 px-4 py-2 rounded-lg border border-purple-500/30 inline-block">Ready to Generate Enhanced Content</h3>
                        <p className="text-sm text-gray-300">
                          {canGenerate 
                            ? `Using ${selectedTemplate?.templateData?.template_type || 'standard'} template with ${enhancedParameters.length} parameters`
                            : "Please complete all required fields"
                          }
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      {(result || isGenerating) && (
                        <Button variant="outline" onClick={resetGeneration}>
                          New Generation
                        </Button>
                      )}
                      
                      
                      <Button
                      type="submit"
                      size="lg"
                      className="bg-linear-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                      onClick={() => console.log('Button clicked:', { canGenerate, disabled: !canGenerate })}
                    >
                        {isGenerating ? (
                          <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Generating...
                          </>
                        ) : (
                          <>
                            <Zap className="h-4 w-4 mr-2" />
                            Generate Content
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </form>
      </Form>

      {/* Enhanced Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-700 dark:text-red-300">
              <AlertCircle className="h-5 w-5" />
              <div>
                <span className="font-medium">Error Generating Content:</span>
                <p className="text-sm mt-1">{error}</p>
                {!USE_BACKEND_API && (
                  <p className="text-xs text-red-600 dark:text-red-400 mt-2">
                    Tip: Enable backend API in environment variables for better reliability
                  </p>
                )}
                {selectedTemplate?.templateData?.template_type && (
                  <p className="text-xs text-gray-500 mt-1">
                    Template Type: {selectedTemplate.templateData.template_type}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generation Preview */}
      <EnhancedGenerationPreview
        isGenerating={isGenerating}
        generatedContent={result?.content}
        onCancel={cancelGeneration}
        onSave={handleViewContent}
        templateName={selectedTemplate?.title}
        styleProfile={selectedStyleProfile?.name}
      />

      <GeneratingDialog open={isGeneratingDialogOpen} />
    </div>
  );
}