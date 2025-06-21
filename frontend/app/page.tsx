"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery, useMutation } from "@tanstack/react-query";
import { generateContentSchema, GenerateContentFormValues } from "@/schemas/generateContentSchema";
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

// ----------------------
// Enhanced Interfaces and Schema
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

interface ContentTemplate {
  id: string;
  name: string;
  description?: string;
  parameters: TemplateParameter[];
}

interface StyleProfile {
  id: string;
  name: string;
  description?: string;
  settings?: Record<string, unknown>;
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

// Use the imported schema instead of defining it here
const formSchema = generateContentSchema;

// ----------------------
// Enhanced Generation Hook
// ----------------------
function useEnhancedGeneration() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<GenerationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const generateContentMutation = useMutation<GeneratedContent, Error, GenerateContentFormValues>({
    mutationFn: async (payload) => {
      setIsGenerating(true);
      setError(null);
      
      console.log("🚀 Sending payload to API:", payload);
      
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.message || "Failed to generate content");
      }
      
      const result = await res.json();
      console.log("✅ API Response:", result);
      return result.data;
    },
    onSuccess: (data: GeneratedContent) => {
      setIsGenerating(false);
      setResult({
        content: data.contentHtml || data.content || "",
        metadata: data.metadata,
        saved_path: data.saved_path,
      });
      console.log("✅ Generation Success:", data);
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
    generateContentMutation.reset();
  };

  const resetGeneration = () => {
    setResult(null);
    setError(null);
    generateContentMutation.reset();
  };

  return {
    isGenerating,
    result,
    error,
    startGeneration,
    cancelGeneration,
    resetGeneration,
  };
}

// ----------------------
// Main Integrated Component
// ----------------------
export default function GenerateContentPage() {
  const [selectedTemplate, setSelectedTemplate] = useState<ContentTemplate | null>(null);
  const [isGeneratingDialogOpen, setIsGeneratingDialogOpen] = useState(false);

  const {
    isGenerating,
    result,
    error,
    startGeneration,
    cancelGeneration,
    resetGeneration,
  } = useEnhancedGeneration();

  // ----------------------
  // Data Queries
  // ----------------------
  const { data: templates = [], isLoading: isLoadingTemplates } = useQuery({
    queryKey: ["templates"],
    queryFn: async () => {
      const res = await fetch("/api/templates");
      const json = await res.json();
      console.log("/api/templates →", json);
      return json.data?.items || json || [];
    },
  });

  const { data: styleProfiles = [], isLoading: isLoadingStyleProfiles } = useQuery({
    queryKey: ["styleProfiles"],
    queryFn: async () => {
      const res = await fetch("/api/style-profiles");
      const json = await res.json();
      console.log("/api/style-profiles →", json);
      return json.data?.items || json || [];
    },
  });

  // ----------------------
  // Form Setup
  // ----------------------
  const form = useForm<GenerateContentFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      templateId: "",
      styleProfileId: "",
      dynamic_parameters: {},
      platform: "substack",
      use_mock: true,
    },
  });

  const watchedTemplate = form.watch("templateId");
  const watchedStyleProfile = form.watch("styleProfileId");

  // Update selected template when form changes
  useEffect(() => {
    const template = templates.find((t: ContentTemplate) => t.id === watchedTemplate);
    setSelectedTemplate(template || null);
    
    if (template && Array.isArray(template.parameters)) {
      const newDefaults: Record<string, string | number | boolean> = {};
      template.parameters.forEach((param: TemplateParameter) => {
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
  }, [watchedTemplate, templates, form]);

  // Sync generating dialog with generation state
  useEffect(() => {
    setIsGeneratingDialogOpen(isGenerating);
  }, [isGenerating]);

  // ----------------------
  // Event Handlers
  // ----------------------
  const onSubmit = (values: GenerateContentFormValues) => {
    console.log("🚀 Form Submitted →", values);
    startGeneration(values);
  };

  const handleSaveContent = () => {
    if (result?.saved_path) {
      const slug = result.saved_path.split("/").pop()?.replace(/\.(json|md)$/, "");
      if (slug) {
        window.location.href = `/content/${slug}`;
      } else {
        console.warn("⚠️ No valid slug found for redirection.");
      }
    }
  };

  const canGenerate = 
    watchedTemplate && 
    watchedStyleProfile && 
    !isGenerating && 
    !isLoadingTemplates && 
    !isLoadingStyleProfiles;

  const selectedStyleProfile = styleProfiles.find((sp: StyleProfile) => sp.id === watchedStyleProfile);

  return (
    <div className="max-w-6xl mx-auto space-y-8 text-gray-900 dark:text-white">
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
                  templates={templates}
                  styleProfiles={styleProfiles}
                  isLoadingTemplates={isLoadingTemplates}
                  isLoadingStyleProfiles={isLoadingStyleProfiles}
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
                  value={watchedStyleProfile}
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
          {selectedTemplate && Array.isArray(selectedTemplate.parameters) && selectedTemplate.parameters.length > 0 && (
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