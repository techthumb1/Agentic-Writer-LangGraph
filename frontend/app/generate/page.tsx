// frontend/app/generate/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useQuery, useMutation } from "@tanstack/react-query";

import { ContentTemplate, StyleProfile, GenerateContentPayload, GeneratedContent } from "@/types";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import ContentEditor from "@/components/content-editor";
import { Loader2 } from "lucide-react"; // npm install lucide-react

// --- Zod Schema for form validation ---
// This schema will be dynamically built based on the selected template's parameters
const formSchema = z.object({
  templateId: z.string().min(1, "Please select a content template."),
  styleProfileId: z.string().min(1, "Please select a style profile."),
  // dynamic_parameters will be an object holding all variable inputs
  dynamic_parameters: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])),
});

type GenerationFormValues = z.infer<typeof formSchema>;

export default function GenerateContentPage() {
  const [selectedTemplate, setSelectedTemplate] = useState<ContentTemplate | null>(null);
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);
  const [isGeneratingDialogOpen, setIsGeneratingDialogOpen] = useState(false);

  // --- Fetch Templates and Style Profiles ---
  const { data: templates, isLoading: isLoadingTemplates } = useQuery<ContentTemplate[]>({
    queryKey: ['templates'],
    queryFn: async () => {
      const res = await fetch('/api/templates');
      if (!res.ok) throw new Error('Failed to fetch templates');
      return res.json();
    },
  });

  const { data: styleProfiles, isLoading: isLoadingStyleProfiles } = useQuery<StyleProfile[]>({
    queryKey: ['styleProfiles'],
    queryFn: async () => {
      const res = await fetch('/api/style-profiles');
      if (!res.ok) throw new Error('Failed to fetch style profiles');
      return res.json();
    },
  });

  // --- Form Hook Initialization ---
  const form = useForm<GenerationFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      templateId: '',
      styleProfileId: '',
      dynamic_parameters: {},
    },
  });

  // --- Update dynamic parameters when template changes ---
  useEffect(() => {
    if (templates && form.watch('templateId')) {
      const template = templates.find(t => t.id === form.watch('templateId'));
      setSelectedTemplate(template || null);

      // Reset dynamic parameters and set defaults for the new template
      const newDynamicParams: Record<string, string | number | boolean> = {};
      template?.parameters.forEach(param => {
        if (param.default !== undefined) {
          newDynamicParams[param.name] = param.default;
        } else {
            // Provide a sensible default if none is specified for the field type
            if (param.type === 'text' || param.type === 'textarea' || param.type === 'select') {
                newDynamicParams[param.name] = '';
            } else if (param.type === 'number') {
                newDynamicParams[param.name] = 0;
            } else if (param.type === 'checkbox') {
                newDynamicParams[param.name] = false;
            }
        }
      });
      form.resetField('dynamic_parameters', { defaultValue: newDynamicParams });
    }
  }, [form.watch('templateId'), templates, form]);


  // --- Mutation Hook for Content Generation ---
  const generateContentMutation = useMutation<GeneratedContent, Error, GenerateContentPayload>({
    mutationFn: async (payload) => {
      setIsGeneratingDialogOpen(true); // Open dialog when mutation starts
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to generate content');
      }
      return res.json();
    },
    onSuccess: (data) => {
      setGeneratedContent(data);
      setIsGeneratingDialogOpen(false); // Close dialog on success
      console.log('Content generated successfully:', data);
    },
    onError: (error) => {
      setIsGeneratingDialogOpen(false); // Close dialog on error
      console.error('Error generating content:', error);
      alert(`Error: ${error.message}`); // Simple error display
    },
  });

  // --- Form Submission Handler ---
  const onSubmit = (values: GenerationFormValues) => {
    const payload: GenerateContentPayload = {
      templateId: values.templateId,
      styleProfileId: values.styleProfileId,
      parameters: values.dynamic_parameters,
    };
    generateContentMutation.mutate(payload);
  };

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
              {/* Template Selection */}
              <FormField
                control={form.control}
                name="templateId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Content Template</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a content template" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {isLoadingTemplates && <SelectItem value="" disabled>Loading templates...</SelectItem>}
                        {templates?.map((template) => (
                          <SelectItem key={template.id} value={template.id}>
                            {template.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>Choose a pre-defined structure for your content.</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Style Profile Selection */}
              <FormField
                control={form.control}
                name="styleProfileId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Style Profile</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a style profile" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {isLoadingStyleProfiles && <SelectItem value="" disabled>Loading styles...</SelectItem>}
                        {styleProfiles?.map((profile) => (
                          <SelectItem key={profile.id} value={profile.id}>
                            {profile.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>Define the tone and style of the generated content.</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </CardContent>
          </Card>

          {/* Dynamic Parameters Card */}
          {selectedTemplate && selectedTemplate.parameters.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Template Parameters</CardTitle>
                <CardDescription>Provide specific inputs for your selected template.</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {selectedTemplate.parameters.map((param) => (
                  <FormField
                    key={param.name}
                    control={form.control}
                    name={`dynamic_parameters.${param.name}`} // Dynamic path
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{param.label}</FormLabel>
                        <FormControl>
                          {param.type === 'text' && (
                            <Input placeholder={param.placeholder} {...field} />
                          )}
                          {param.type === 'textarea' && (
                            <Textarea placeholder={param.placeholder} {...field} />
                          )}
                          {param.type === 'number' && (
                            <Input type="number" placeholder={param.placeholder} {...field} onChange={e => field.onChange(Number(e.target.value))} />
                          )}
                          {param.type === 'select' && param.options && (
                            <Select onValueChange={field.onChange} defaultValue={field.value as string}>
                              <SelectTrigger>
                                <SelectValue placeholder={`Select ${param.label}`} />
                              </SelectTrigger>
                              <SelectContent>
                                {param.options.map(option => (
                                  <SelectItem key={option} value={option}>{option}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          )}
                          {/* Add other types like checkbox if needed */}
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                ))}
              </CardContent>
            </Card>
          )}

          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white text-lg py-3"
            disabled={generateContentMutation.isPending || isLoadingTemplates || isLoadingStyleProfiles || !form.formState.isValid}
          >
            {generateContentMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Generating Content...
              </>
            ) : (
              'Generate Content'
            )}
          </Button>
        </form>
      </Form>

      {/* Generated Content Display */}
      {generatedContent && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Generated Content</CardTitle>
            <CardDescription>Review and refine the AI-generated output.</CardDescription>
          </CardHeader>
          <CardContent>
            <h2 className="text-2xl font-bold mb-4">{generatedContent.title}</h2>
            <ContentEditor content={generatedContent.contentHtml} editable={true} />
            {/* Future: Add buttons to Save, Publish, Copy, etc. */}
          </CardContent>
        </Card>
      )}

      {/* Generating Content Dialog (Optional, but good for UX) */}
      <Dialog open={isGeneratingDialogOpen} onOpenChange={setIsGeneratingDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Generating Content...</DialogTitle>
            <DialogDescription>
              Please wait while our AI agents are crafting your content. This may take a moment.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-center items-center py-8">
            <Loader2 className="h-10 w-10 animate-spin text-blue-500" />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
