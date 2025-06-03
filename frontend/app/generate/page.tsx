"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery, useMutation } from "@tanstack/react-query";
import * as z from "zod";
//import { useRouter } from "next/navigation";

import { Form } from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loader2 } from "lucide-react";

import TemplateSelector from "@/components/TemplateSelector";
import DynamicParameters from "@/components/DynamicParameters";
import GeneratedContentDisplay from "@/components/GeneratedContentDisplay";
import GeneratingDialog from "@/components/GeneratingDialog";

// ----------------------
// Interfaces and Schema
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

interface GeneratedContent {
  id?: string;
  title: string;
  contentHtml: string;
  metadata?: Record<string, unknown>;
}

const formSchema = z.object({
  templateId: z.string().min(1, "Please select a content template."),
  styleProfileId: z.string().min(1, "Please select a style profile."),
  dynamic_parameters: z.record(
    z.string(),
    z.union([z.string(), z.number(), z.boolean()])
  ),
});

type GenerateContentFormValues = z.infer<typeof formSchema>;

// ----------------------
// Main Component
// ----------------------

export default function GenerateContentPage() {
  const [selectedTemplate, setSelectedTemplate] = useState<ContentTemplate | null>(null);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);
  const [isGeneratingDialogOpen, setIsGeneratingDialogOpen] = useState(false);
  //const router = useRouter();

  // ----------------------
  // Queries
  // ----------------------

  const { data: templates = [], isLoading: isLoadingTemplates } = useQuery({
    queryKey: ["templates"],
    queryFn: async () => {
      const res = await fetch("/api/templates");
      const json = await res.json();
      console.log("🔍 /api/templates →", json);
      return json.data?.items || json || [];
    },
  });

  const { data: styleProfiles = [], isLoading: isLoadingStyleProfiles } = useQuery({
    queryKey: ["styleProfiles"],
    queryFn: async () => {
      const res = await fetch("/api/style-profiles");
      const json = await res.json();
      console.log("🔍 /api/style-profiles →", json);
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
    },
  });

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

  // ----------------------
  // Mutation
  // ----------------------

  const generateContentMutation = useMutation<GeneratedContent, Error, GenerateContentFormValues>({
    mutationFn: async (payload) => {
      setIsGeneratingDialogOpen(true);
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Failed to generate content");
      return res.json();
    },

    onSuccess: (data: GeneratedContent & { saved_path?: string }) => {
      console.log("✅ Mutation Success:", data);
      setGeneratedContent(data);
      setIsGeneratingDialogOpen(false);

      console.log("🧾 Holding at /generate with contentHtml:");
      console.log(data?.contentHtml);
          
      // comment out redirection for now
      // const savedPath = data?.saved_path;
      // const contentID = savedPath?.split("/").pop()?.replace(".md", "");
      // if (contentID) {
      //   router.push(`/content/${contentID}`);
      // }

    },

    onError: (error) => {
      setIsGeneratingDialogOpen(false);
      const message =
        error instanceof Error
          ? error.message
          : typeof error === "object" && error !== null && "message" in error
          ? (error as { message: string }).message
          : "An unknown error occurred during generation.";

      console.error("❌ Mutation error:", error);
      alert(`Error: ${message}`);
    },
  });         

  const onSubmit = (values: GenerateContentFormValues) => {
    console.log("🚀 Form Submitted →", values);
    generateContentMutation.mutate(values);
  };

  return (
    <div className="space-y-8">
      <h1 className="text-4xl font-bold text-gray-900">Generate New Content</h1>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Content Configuration</CardTitle>
              <CardDescription>
                Select a template and style profile for your content.
              </CardDescription>
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

          {selectedTemplate && Array.isArray(selectedTemplate.parameters) && selectedTemplate.parameters.length > 0 && (

            <Card>
              <CardHeader>
                <CardTitle>Template Parameters</CardTitle>
                <CardDescription>
                  Provide specific inputs for your selected template.
                </CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <DynamicParameters parameters={selectedTemplate?.parameters ?? []} />

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

      {/* Display Output */}
<GeneratedContentDisplay
  generatedContent={generatedContent?.contentHtml ?? "<h2>No content passed</h2>"}
  isLoading={generateContentMutation.isPending}
/>


      <GeneratingDialog open={isGeneratingDialogOpen} />
    </div>
  );
}
