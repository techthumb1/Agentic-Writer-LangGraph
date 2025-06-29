"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loader2, Sparkles, Settings, Zap } from "lucide-react";
import TemplateSelector from "@/components/TemplateSelector";
import StyleProfilesSelector from "@/components/StyleProfilesSelector";
import DynamicParameters from "@/components/DynamicParameters";
import GeneratingDialog from "@/components/GeneratingDialog";
import { GenerationPreview } from "@/components/GenerationPreview";
import { GenerateContentFormValues, generateContentSchema } from "@/schemas/generateContentSchema";
import { useTemplates } from "@/hooks/useTemplates";
import { useStyleProfiles } from "@/hooks/useStyleProfiles";
import { 
  adaptTemplateCollection, 
  adaptStyleProfileCollection 
} from "@/utils/typeAdapters";

// ----------------------
// Enhanced Interfaces
// ----------------------
interface TemplateParameter {
  name: string;
  label: string;
  type: "text" | "textarea" | "number" | "select" | "checkbox";
  placeholder?: string;
  default?: string | number | boolean;
  options?: string[];
  required?: boolean;
}

// Extended template interface that includes parameters
interface ExtendedTemplate {
  id: string;
  name: string;
  description?: string;
  category?: string;
  sections?: string[];
  metadata?: Record<string, unknown>;
  filename?: string;
  parameters?: TemplateParameter[]; // Make parameters optional since API templates might not have them
}

// Extended style profile interface
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

interface GeneratedContent {
  id?: string;
  title: string;
  contentHtml: string;
  content?: string;
  metadata?: Record<string, unknown>;
  saved_path?: string;
}

interface GenerationResult {
  content: string;
  metadata?: Record<string, unknown>;
  saved_path?: string;
}

// ----------------------
// Enhanced Generation Hook with Async Polling
// ----------------------
function useEnhancedGeneration() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);

  // Polling function to check generation status
  const pollGenerationStatus = async (requestId: string): Promise<GeneratedContent> => {
    const maxAttempts = 60; // Poll for up to 5 minutes (60 * 5s intervals)
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const statusRes = await fetch(`/api/generate/status/${requestId}`);
        
        if (!statusRes.ok) {
          throw new Error(`Status check failed: ${statusRes.status}`);
        }

        const statusData = await statusRes.json();

        if (statusData.status === 'completed') {
          return statusData.data;
        } else if (statusData.status === 'failed') {
          throw new Error(statusData.error || 'Generation failed');
        } else if (statusData.status === 'pending' || statusData.status === 'processing') {
          // Still processing, wait and try again
          await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
          attempts++;
        } else {
          throw new Error(`Unknown status: ${statusData.status}`);
        }
      } catch (error) {
        console.error(`❌ Polling error on attempt ${attempts + 1}:`, error);
        if (attempts >= maxAttempts - 1) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, 5000));
        attempts++;
      }
    }

    throw new Error('Generation timed out after 5 minutes');
  };

  const generateContentMutation = useMutation<GeneratedContent, Error, GenerateContentFormValues>({
    mutationFn: async (payload) => {
      setIsGenerating(true);
      setError(null);
      setRequestId(null);
      
      console.log('🚀 Starting generation with payload:', payload);

      const payloadForBackend = {
        template: payload.templateId,
        style_profile: payload.styleProfileId,
        dynamic_parameters: payload.dynamic_parameters || {},
        priority: 1,
        timeout_seconds: 300,
        platform: payload.platform || "web",
        use_mock: payload.use_mock || false,
      };
      
      console.log('📤 Sending to backend:', payloadForBackend);
      
      // Step 1: Start the generation
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(payloadForBackend),
      });
      
      console.log('📥 Response status:', res.status);
      
      if (!res.ok) {
        const errorText = await res.text();
        console.error("🔍 Error response body:", errorText);
        
        try {
          const errorData = JSON.parse(errorText);
          throw new Error(errorData.detail || errorData.message || "Failed to start generation");
        } catch {
          throw new Error(`HTTP ${res.status}: ${errorText}`);
        }
      }
      
      const initialResponse = await res.json();
      console.log('📄 Initial response:', initialResponse);

      // Check if we got the content immediately (synchronous response)
      if (initialResponse.data && initialResponse.status !== 'pending') {
        return initialResponse.data;
      }

      // If we have a request_id, poll for completion (asynchronous response)
      if (initialResponse.request_id) {
        setRequestId(initialResponse.request_id);
        return await pollGenerationStatus(initialResponse.request_id);
      }

      // If neither, something's wrong
      throw new Error("No content or request ID returned from API");
    },
    onSuccess: (data: GeneratedContent) => {
      setIsGenerating(false);
      setResult({
        content: data.contentHtml || data.content || "",
        metadata: data.metadata,
        saved_path: data.saved_path,
      });
      console.log('✅ Generation completed successfully');
    },
    onError: (error) => {
      setIsGenerating(false);
      const message = error instanceof Error ? error.message : "An unknown error occurred during generation.";
      setError(message);
      console.error("❌ Generation error:", error);
    },
  });

  const startGeneration = (params: GenerateContentFormValues) => {
    generateContentMutation.mutate(params);
  };

  const cancelGeneration = () => {
    setIsGenerating(false);
    setRequestId(null);
    generateContentMutation.reset();
  };

  const resetGeneration = () => {
    setResult(null);
    setError(null);
    setRequestId(null);
    generateContentMutation.reset();
  };

  return {
    isGenerating,
    result,
    error,
    requestId,
    startGeneration,
    cancelGeneration,
    resetGeneration,
  };
}

// ----------------------
// Main Integrated Component
// ----------------------
export default function GeneratePage() {
  // State for generating dialog
  const [isGeneratingDialogOpen, setIsGeneratingDialogOpen] = useState(false);
  
  // Use the updated hooks
  const { templates, isLoading: templatesLoading, isError: templatesError, error: templatesErrorDetails } = useTemplates();
  const { styleProfiles, isLoading: profilesLoading, isError: profilesError } = useStyleProfiles();

  const {
    isGenerating,
    result,
    error,
    startGeneration,
    cancelGeneration,
    resetGeneration,
  } = useEnhancedGeneration();

  // ----------------------
  // Form Setup - Using backend-compatible schema
  // ----------------------
  const form = useForm<GenerateContentFormValues>({
    resolver: zodResolver(generateContentSchema),
    defaultValues: {
      templateId: "",
      styleProfileId: "",
      dynamic_parameters: {},
      platform: "web",
      use_mock: false,
    },
    mode: "onChange",
  });

  const watchedTemplateId = form.watch("templateId");
  const watchedStyleProfileId = form.watch("styleProfileId");

  // Safe template and style profile finding
  const selectedTemplate: ExtendedTemplate | null = templates && Array.isArray(templates) 
    ? templates.find((t: ExtendedTemplate) => t.id === watchedTemplateId) || null
    : null;
    
  const selectedStyleProfile: ExtendedStyleProfile | null = styleProfiles && Array.isArray(styleProfiles)
    ? styleProfiles.find((sp: ExtendedStyleProfile) => sp.id === watchedStyleProfileId) || null
    : null;

  // Debug logging
  console.log('🔍 Debug info:', {
    templates: templates?.length || 0,
    styleProfiles: styleProfiles?.length || 0,
    selectedTemplate: selectedTemplate?.name,
    selectedStyleProfile: selectedStyleProfile?.name,
    watchedTemplateId,
    watchedStyleProfileId
  });

  // Update selected template when form changes
  useEffect(() => {
    if (selectedTemplate && selectedTemplate.parameters && Array.isArray(selectedTemplate.parameters)) {
      const newDefaults: Record<string, string | number | boolean> = {};
      selectedTemplate.parameters.forEach((param: TemplateParameter) => {
        if (param.default !== undefined) {
          newDefaults[param.name] = param.default;
        } else {
          switch (param.type) {
            case "text":
            case "textarea":
            case "select":
              newDefaults[param.name] = "";
              break;
            case "number":
              newDefaults[param.name] = 0;
              break;
            case "checkbox":
              newDefaults[param.name] = false;
              break;
          }
        }
      });
      form.resetField("dynamic_parameters", { defaultValue: newDefaults });
    }
  }, [watchedTemplateId, selectedTemplate, form]);

  // Sync generating dialog with generation state
  useEffect(() => {
    setIsGeneratingDialogOpen(isGenerating);
  }, [isGenerating]);

  // Loading states
  if (templatesLoading || profilesLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading templates and style profiles...</p>
        </div>
      </div>
    );
  }

  // Error states
  if (templatesError || profilesError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <h2 className="text-xl font-bold mb-2">Error Loading Data</h2>
          <p className="mb-4">
            {templatesError && "Failed to load templates. "}
            {profilesError && "Failed to load style profiles."}
          </p>
          <p className="text-sm text-gray-500 mb-4">
            {templatesErrorDetails?.message}
          </p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // No data states
  if (!templates || !Array.isArray(templates) || templates.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-bold mb-2">No Templates Available</h2>
          <p className="text-gray-600 mb-4">
            Templates: {templates?.length || 0} | Type: {typeof templates}
          </p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Refresh
          </button>
        </div>
      </div>
    );
  }

  // ----------------------
  // Event Handlers
  // ----------------------
  const onSubmit = (values: GenerateContentFormValues) => {
    console.log('📝 Form submitted:', values);
    startGeneration(values);
  };

  const handleSaveContent = () => {
    if (result?.saved_path) {
      const slug = result.saved_path.split("/").pop()?.replace(/\.(json|md)$/, "");
      if (slug) {
        window.location.href = `/content/${slug}`;
      }
    }
  };

  const canGenerate = 
    watchedTemplateId && 
    watchedStyleProfileId && 
    !isGenerating && 
    !templatesLoading && 
    !profilesLoading;

  return (
    <div className="max-w-6xl mx-auto space-y-8 text-gray-900 dark:text-white">
      {/* Debug info (remove after fixing) */}
      <div className="mb-4 p-4 bg-gray-100 dark:bg-gray-800 rounded text-xs">
        <p>📊 Debug: {templates?.length || 0} templates, {styleProfiles?.length || 0} profiles loaded</p>
        <p>🎯 Selected: {selectedTemplate?.name || 'None'} | {selectedStyleProfile?.name || 'None'}</p>
        <p>🔍 Watching: {watchedTemplateId} | {watchedStyleProfileId}</p>
      </div>

      {/* Enhanced Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          Generate AI Content
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Create high-quality content using our advanced AI models. Select a template and style profile to get started.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          {/* Configuration Section */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Template Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-purple-600" />
                  Content Template
                </CardTitle>
                <CardDescription>
                  Choose the type of content you want to generate.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TemplateSelector
                  form={form}
                  // FIXED VERSION:
                templates={adaptTemplateCollection(templates || [])}
                styleProfiles={adaptStyleProfileCollection(styleProfiles || [])}
                  isLoadingTemplates={templatesLoading}
                  isLoadingStyleProfiles={profilesLoading}
                />
                {selectedTemplate && (
                  <div className="mt-4">
                    <Badge variant="secondary" className="mb-2">
                      Selected Template
                    </Badge>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {selectedTemplate.description || selectedTemplate.name}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Style Profile Selection */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5 text-purple-600" />
                  Style Profile
                </CardTitle>
                <CardDescription>
                  Define the tone and style of your content.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <StyleProfilesSelector
                  value={watchedStyleProfileId}
                  onChange={(value: string) => form.setValue("styleProfileId", value)}
                />
                {selectedStyleProfile && (
                  <div className="mt-4">
                    <Badge variant="secondary" className="mb-2">
                      Selected Style
                    </Badge>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {selectedStyleProfile.description || selectedStyleProfile.name}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Dynamic Parameters */}
          {selectedTemplate && selectedTemplate.parameters && Array.isArray(selectedTemplate.parameters) && selectedTemplate.parameters.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Template Parameters</CardTitle>
                <CardDescription>
                  Provide specific inputs for your selected template.
                </CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <DynamicParameters parameters={selectedTemplate.parameters} />
              </CardContent>
            </Card>
          )}

          {/* Generation Controls */}
          <Card className="border-2 border-dashed border-purple-200 dark:border-purple-800">
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                    <Zap className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Ready to Generate</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {canGenerate 
                        ? "Click generate to create your content"
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
                        Generate Content
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </form>
      </Form>

      {/* Error Display */}
      {error && (
        <Card className="border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-700 dark:text-red-300">
              <span className="font-medium">Generation Failed:</span>
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generation Preview */}
      <GenerationPreview
        isGenerating={isGenerating}
        generatedContent={result?.content}
        onCancel={cancelGeneration}
        onSave={handleSaveContent}
        templateName={selectedTemplate?.name}
        styleProfile={selectedStyleProfile?.name}
      />

      {/* Enhanced Generating Dialog */}
      <GeneratingDialog open={isGeneratingDialogOpen} />
    </div>
  );
}