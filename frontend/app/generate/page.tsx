// frontend/app/generate/page.tsx

"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery, useMutation } from "@tanstack/react-query";
import * as z from "zod";

import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2 } from "lucide-react";

import TemplateSelector from "@/components/TemplateSelector";
import DynamicParameters from "@/components/DynamicParameters";
import GeneratedContentDisplay from "@/components/GeneratedContentDisplay";
import GeneratingDialog from "@/components/GeneratingDialog";

// Interfaces
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

//interface StyleProfile {
//  id: string;
//  name: string;
//  description?: string;
//}

interface GeneratedContent {
  id?: string;
  title: string;
  contentHtml: string;
  metadata?: Record<string, unknown>;
}

// REMOVE GenerateContentPayload entirely — not needed


// Form Schema
const formSchema = z.object({
  templateId: z.string().min(1, "Please select a content template."),
  styleProfileId: z.string().min(1, "Please select a style profile."),
  dynamic_parameters: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])),
});

type GenerateContentFormValues = z.infer<typeof formSchema>;

export default function GenerateContentPage() {
  const [selectedTemplate, setSelectedTemplate] = useState<ContentTemplate | null>(null);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);
  const [isGeneratingDialogOpen, setIsGeneratingDialogOpen] = useState(false);

  // Fetch templates
  const { data: templates = [], isLoading: isLoadingTemplates } = useQuery({
    queryKey: ['templates'],
    queryFn: async () => {
      const res = await fetch('/api/templates');
      const json = await res.json();
      console.log("🔍 /api/templates →", json);
      return json.data?.items || [];  
    },
  });



  // Fetch style profiles
  const { data: styleProfiles = [], isLoading: isLoadingStyleProfiles } = useQuery({
    queryKey: ['styleProfiles'],
    queryFn: async () => {
      const res = await fetch('/api/style-profiles');
      const json = await res.json();
      console.log("🔍 /api/style-profiles →", json);
      return json.data?.items || [];  // defensive fallback
    },
  });




  // Setup form
  const form = useForm<GenerateContentFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      templateId: "",
      styleProfileId: "",
      dynamic_parameters: {},
    },
  });

  // Watch and update template-specific parameters
  const watchedTemplateId = form.watch("templateId");

  useEffect(() => {
    const template = templates.find((t: ContentTemplate) => t.id === watchedTemplateId);
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
  }, [watchedTemplateId, templates, form]);

  // Content generation mutation
  const generateContentMutation = useMutation<GeneratedContent, Error, GenerateContentFormValues>({
    mutationFn: async (payload) => {
      setIsGeneratingDialogOpen(true);
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.message || "Generation failed");
      }
      return res.json();
    },
    onSuccess: (data) => {
      setGeneratedContent(data);
      setIsGeneratingDialogOpen(false);
    },
    onError: (error) => {
      setIsGeneratingDialogOpen(false);
      alert(`Error: ${error.message}`);
    },
  });

  const onSubmit = (values: GenerateContentFormValues) => {
    generateContentMutation.mutate(values);
  };
  console.log("🧪 templates:", templates);
  console.log("🧪 styleProfiles:", styleProfiles);

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold text-gray-900">Generate New Content</h1>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Content Configuration</CardTitle>
              <CardDescription>Select a template and style profile for your content.</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <TemplateSelector
                form={form}
                templates={templates}
                styleProfiles={styleProfiles}
                isLoadingTemplates={isLoadingTemplates}
                isLoadingStyleProfiles={isLoadingStyleProfiles}
              />
            </CardContent>
          </Card>

          {selectedTemplate?.parameters?.length && selectedTemplate.parameters.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Template Parameters</CardTitle>
                <CardDescription>Provide specific inputs for your selected template.</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <DynamicParameters parameters={selectedTemplate.parameters} />
              </CardContent>
            </Card>
          )}

          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white text-lg py-3"
            disabled={
              generateContentMutation.isPending ||
              isLoadingTemplates ||
              isLoadingStyleProfiles ||
              !form.formState.isValid
            }
          >
            {generateContentMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Generating Content...
              </>
            ) : (
              "Generate Content"
            )}
          </Button>
        </form>
      </Form>

      {generatedContent && (
        <GeneratedContentDisplay
          generatedContent={generatedContent.contentHtml}
          isLoading={generateContentMutation.isPending}
        />
      )}

      <GeneratingDialog open={isGeneratingDialogOpen} />
    </div>
  );
}
