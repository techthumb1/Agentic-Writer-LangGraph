"use client";
import { FormField } from "@/components/ui/form";
import React, { useState, useEffect, useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form } from "@/components/ui/form";
import { SubmitHandler } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { useEnhancedGeneration } from "@/hooks/useEnhancedGeneration";
import { useSettings } from '@/lib/settings-context'
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
  Save,
  Palette, 
  Eye, 
  FileText, 
  Loader2, 
  Sparkles, 
  Zap, 
  AlertCircle,
  Settings,
  Info
} from "lucide-react";

import TemplateSelector from "@/components/TemplateSelector";
import DynamicParameters from "@/components/DynamicParameters";
import { useQueryClient } from "@tanstack/react-query";
import GeneratingDialog from "@/components/GeneratingDialog";
import { useTemplates } from "@/hooks/useTemplates";
import StyleProfilesSelector from "@/components/StyleProfilesSelector";
import { useStyleProfiles } from "@/hooks/useStyleProfiles";
import { z } from "zod";

// Schema Definition
const generateContentSchema = z.object({
  templateId: z.string().min(1),
  styleProfileId: z.string().min(1),
  dynamic_parameters: z.record(z.union([z.string(), z.number(), z.boolean()])),
  platform: z.string(),
});

type GenerateContentFormValues = z.infer<typeof generateContentSchema>;

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

// Enhanced Generation Preview Component
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
            className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
          >
            <Save className="h-4 w-4 mr-2" />
            Save Content
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
  const [isGeneratingDialogOpen, setIsGeneratingDialogOpen] = useState(false);
  
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

  // Enhanced template and style profile finding with enhanced structure support
  const selectedTemplate: Template | null = templates && Array.isArray(templates) && watchedTemplateId
    ? templates.find((t: Template) => t && t.id === watchedTemplateId) || null
    : null;

  console.log('🔍 Enhanced Template Selection:', {
      watchedTemplateId,
      templatesCount: templates?.length,
      selectedTemplate: selectedTemplate ? {
        id: selectedTemplate.id,
        title: selectedTemplate.title,
        templateType: selectedTemplate.templateData?.template_type,
        sectionsCount: selectedTemplate.templateData?.sections?.length || 0,
        parametersCount: Object.keys(selectedTemplate.templateData?.parameters || {}).length,
        hasInstructions: !!selectedTemplate.templateData?.instructions,
        isEnhanced: selectedTemplate.templateData?.template_type !== 'legacy'
      } : null,
    });
    
  const selectedStyleProfile: ExtendedStyleProfile | null = styleProfiles && Array.isArray(styleProfiles) && watchedStyleProfileId
    ? styleProfiles.find((sp: ExtendedStyleProfile) => sp && sp.id === watchedStyleProfileId) || null
    : null;

  const queryClient = useQueryClient();
  const { generationSettings } = useSettings();

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

// frontend/app/generate/page.tsx - AUTO-SAVE DEPENDENCY FIX
// Replace existing auto-save logic with this fixed implementation
// Eliminates React warning and ensures reliable auto-save to generated_content folder

// REPLACE the existing autoSaveToGeneratedContentFolder useCallback with this:
const autoSaveToGeneratedContentFolder = useCallback(async () => {
  if (!result?.content) return;
  
  try {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
    const templateSlug = selectedTemplate?.id || 'content';
    const filename = `${templateSlug}_${timestamp}_${Date.now()}`;
  
    const response = await fetch('/api/content/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: result.content,
        filename: filename,
        metadata: {
          template: selectedTemplate?.id,
          style_profile: selectedStyleProfile?.id,
          word_count: result.content.split(' ').length,
          created_at: new Date().toISOString(),
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Save failed: ${response.status}`);
    }

    console.log('Auto-saved to generated_content folder:', filename);
  } catch (error) {
    console.error('Auto-save failed:', error);
  }
}, [result?.content, selectedTemplate?.id, selectedStyleProfile?.id]);

// REPLACE the existing useEffect with this fixed version:
useEffect(() => {
  if (result?.content && generationSettings.autoSave && !isGenerating) {
    // Delay auto-save to ensure generation is complete
    const saveTimeout = setTimeout(() => {
      autoSaveToGeneratedContentFolder();
    }, 2000);

    return () => clearTimeout(saveTimeout);
  }
}, [result?.content, isGenerating, generationSettings.autoSave, autoSaveToGeneratedContentFolder]);
  // Enhanced template parameters handling with dynamic structure support
  useEffect(() => {
    if (selectedTemplate?.templateData?.parameters && typeof selectedTemplate.templateData.parameters === 'object') {
      try {
        const newDefaults: Record<string, string | number | boolean> = {};

        // Handle enhanced template parameter structure
        Object.entries(selectedTemplate.templateData.parameters).forEach(([paramName, param]) => {
          if (!param || typeof param !== 'object' || !paramName) {
            console.warn('Invalid enhanced parameter:', param);
            return;
          }

          const typedParam = param as { default?: unknown; type?: string; [key: string]: unknown };
          
          // Only assign if the default is string | number | boolean
          if (
            typeof typedParam.default === "string" ||
            typeof typedParam.default === "number" ||
            typeof typedParam.default === "boolean"
          ) {
            newDefaults[paramName] = typedParam.default;
          } else if (Array.isArray(typedParam.default) && typedParam.default.length > 0 && typeof typedParam.default[0] === "string") {
            // If the default is a string array, use the first value or empty string
            newDefaults[paramName] = typedParam.default[0];
          } else {
            // Fallback based on parameter type
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

        // FIX: Set defaults properly in form state
        form.setValue("dynamic_parameters", newDefaults);

        // Force form to recognize the new values
        Object.entries(newDefaults).forEach(([key, value]) => {
          form.setValue(`dynamic_parameters.${key}`, value);
        });

      } catch (error) {
        console.error('Error processing enhanced template parameters:', error);
      }
    } else {
      // Clear parameters if no template selected
      form.setValue("dynamic_parameters", {});
    }
  }, [watchedTemplateId, selectedTemplate, form]);
  
  useEffect(() => {
    setIsGeneratingDialogOpen(isGenerating);
  }, [isGenerating]);

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

  // File: frontend/app/generate/page.tsx
  // FIND the existing onSubmit function and REPLACE with this enhanced version:
  const onSubmit: SubmitHandler<GenerateContentFormValues> = async (values) => {
    console.log('🔍 Enhanced form submitted with values:', values);
    console.log('🔍 Enhanced dynamic parameters:', values.dynamic_parameters);
    console.log('🔍 Selected enhanced template:', selectedTemplate?.templateData?.template_type);

    const params = values.dynamic_parameters || {};

    // Use user's generation settings (moved to component level)
    console.log('⚙️ Using generation settings:', generationSettings);
    console.log('⚙️ Using generation settings:', generationSettings);

    console.log('🔍 Raw enhanced form parameters:', params);
    console.log('✅ Starting enhanced generation with all parameters...');

    // Enhanced generation request with template configuration AND user settings
    type GenerationMode = "standard" | "premium" | "enterprise" | undefined;
    const generationMode: GenerationMode = 
      selectedTemplate?.templateData?.generation_mode === "standard" ||
      selectedTemplate?.templateData?.generation_mode === "premium" ||
      selectedTemplate?.templateData?.generation_mode === "enterprise"
        ? selectedTemplate.templateData.generation_mode
        : "standard";

    // Apply user's settings to parameters
    const enhancedParametersWithSettings = {
      ...params,
      // Content length from user settings
      preferred_length: getLengthFromTokens(generationSettings.maxTokens),
      // Creativity level from user settings
      creativity_level: getCreativityLevel(generationSettings.temperature),
      // Content quality preference
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

      // User's generation settings
      generation_settings: {
        max_tokens: generationSettings.maxTokens,
        temperature: generationSettings.temperature,
        quality_mode: generationSettings.contentQuality,
        auto_save: generationSettings.autoSave,
      },

      // Enhanced template configuration
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
  };

  // ADD these helper functions after the onSubmit function:

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

  type GenerationResultMetadata = {
    saved_path?: string;
    [key: string]: unknown;
  };

  const handleSaveContent = () => {
    if (result && 'metadata' in result && result.metadata) {
      const savedPath = (result.metadata as GenerationResultMetadata)?.saved_path;
      if (savedPath) {
        const slug = savedPath.split("/").pop()?.replace(/\.(json|md)$/, "");
        if (slug) {
          window.location.href = `/content/${slug}`;
          return;
        }
      }
    }
    
    window.location.href = '/content';
  };

  const canGenerate = 
    watchedTemplateId && 
    watchedStyleProfileId && 
    !isGenerating && 
    !templatesLoading && 
    !profilesLoading;

  // Get enhanced parameters for display - convert Template to ContentTemplate format
  const enhancedParameters = selectedTemplate && selectedTemplate.templateData?.parameters ? 
    Object.entries(selectedTemplate.templateData.parameters).map(([key, param]) => {
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
    }) : [];

  return (
    <div className="max-w-6xl mx-auto space-y-8 text-gray-900 dark:text-white">
      {/* Enhanced Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          Generate Enhanced AI Content
        </h1>
        <p className="text-lg text-white max-w-2xl mx-auto">
          Create high-quality content using our advanced AI models with enhanced dynamic templates. 
          Select a template and style profile to get started.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Enhanced Template Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  Content Template
                </CardTitle>
                <CardDescription>
                  Choose from our collection of dynamic, enhanced templates.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TemplateSelector
                  form={form}
                  templates={templates}
                  isLoadingTemplates={templatesLoading}
                />
              </CardContent>
            </Card>

            {/* Style Profile Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="h-5 w-5 text-purple-600" />
                  Style Profile
                </CardTitle>
                <CardDescription>
                  Define the tone and style of your content.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <StyleProfilesSelector
                  value={watchedStyleProfileId}
                  onChange={(styleId) => form.setValue('styleProfileId', styleId)}
                  label=""
                  required={true}
                  showDescription={true}
                  disabled={profilesLoading}
                />
              </CardContent>
            </Card>
          </div>
          {/* Enhanced Dynamic Parameters */}
          {selectedTemplate && enhancedParameters.length > 0 && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="h-5 w-5 text-purple-600" />
                      Template Parameters
                    </CardTitle>
                    <CardDescription>
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
                <FormField
                  control={form.control}
                  name="dynamic_parameters"
                  render={() => (
                    <DynamicParameters parameters={enhancedParameters} />
                  )}
                />
              </CardContent>
            </Card>
          )}

          {/* Enhanced Template Information */}
          {selectedTemplate && selectedTemplate.templateData && (
            <Card className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950 border-purple-200 dark:border-purple-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-purple-800 dark:text-purple-200">
                  <Info className="h-5 w-5" />
                  Template Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-sm text-purple-700 dark:text-purple-300">Template Type</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {selectedTemplate.templateData.template_type || 'Standard'}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-sm text-purple-700 dark:text-purple-300">Generation Mode</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {selectedTemplate.templateData.generation_mode || 'Standard'}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-sm text-purple-700 dark:text-purple-300">Content Sections</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {selectedTemplate.templateData.sections?.length || 0} sections defined
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-sm text-purple-700 dark:text-purple-300">Output Format</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {selectedTemplate.templateData.content_format || 'Standard'}
                    </p>
                  </div>
                </div>
                
                {selectedTemplate.templateData.instructions && (
                  <div>
                    <h4 className="font-medium text-sm text-purple-700 dark:text-purple-300 mb-2">
                      Template Instructions
                    </h4>
                    <div className="text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-900 p-3 rounded border max-h-32 overflow-y-auto">
                      {selectedTemplate.templateData.instructions.slice(0, 300)}
                      {selectedTemplate.templateData.instructions.length > 300 && '...'}
                    </div>
                  </div>
                )}

                {/* Section Order Preview */}
                {selectedTemplate.templateData.section_order && selectedTemplate.templateData.section_order.length > 0 && (
                  <div>
                    <h4 className="font-medium text-sm text-purple-700 dark:text-purple-300 mb-2">
                      Section Order
                    </h4>
                    <div className="flex flex-wrap gap-1">
                      {selectedTemplate.templateData.section_order.slice(0, 8).map((section, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {index + 1}. {section.replace(/_/g, ' ')}
                        </Badge>
                      ))}
                      {selectedTemplate.templateData.section_order.length > 8 && (
                        <Badge variant="outline" className="text-xs">
                          +{selectedTemplate.templateData.section_order.length - 8} more
                        </Badge>
                      )}
                    </div>
                  </div>
                )}

                {/* Validation Rules Preview */}
                {selectedTemplate.templateData.validation_rules && selectedTemplate.templateData.validation_rules.length > 0 && (
                  <div>
                    <h4 className="font-medium text-sm text-purple-700 dark:text-purple-300 mb-2">
                      Validation Rules ({selectedTemplate.templateData.validation_rules.length})
                    </h4>
                    <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                      {selectedTemplate.templateData.validation_rules.slice(0, 3).map((rule, index) => (
                        <div key={index} className="flex items-center gap-2">
                          <div className="w-1 h-1 bg-purple-400 rounded-full"></div>
                          <span>{rule}</span>
                        </div>
                      ))}
                      {selectedTemplate.templateData.validation_rules.length > 3 && (
                        <div className="flex items-center gap-2 text-gray-500">
                          <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                          <span>+{selectedTemplate.templateData.validation_rules.length - 3} more rules...</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Enhanced Generation Button */}
          <Card className="border-2 border-dashed border-purple-200 dark:border-purple-800">
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                    <Zap className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Ready to Generate Enhanced Content</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {canGenerate 
                        ? `Using ${selectedTemplate?.templateData?.template_type || 'standard'} template with ${enhancedParameters.length} parameters`
                        : "Please select both template and style profile"
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
                    disabled={!canGenerate}
                    size="lg"
                    className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Zap className="h-4 w-4 mr-2" />
                        Generate Enhanced Content
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </form>
      </Form>

      {/* Enhanced Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-700 dark:text-red-300">
              <AlertCircle className="h-5 w-5" />
              <div>
                <span className="font-medium">Enhanced Generation Failed:</span>
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

      {/* Enhanced Generation Preview */}
      <EnhancedGenerationPreview
        isGenerating={isGenerating}
        generatedContent={result?.content}
        onCancel={cancelGeneration}
        onSave={handleSaveContent}
        templateName={selectedTemplate?.title}
        styleProfile={selectedStyleProfile?.name}
      />

      <GeneratingDialog open={isGeneratingDialogOpen} />
    </div>
  );
}