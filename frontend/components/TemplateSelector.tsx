// frontend/components/TemplateSelector.tsx
"use client";

import React from "react";
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { ContentTemplate, StyleProfile } from "@/types/content";
import { UseFormReturn } from "react-hook-form";
import { GenerateContentFormValues } from "@/schemas/generateContentSchema";

interface TemplateSelectorProps {
  form: UseFormReturn<GenerateContentFormValues>;
  templates: ContentTemplate[];
  styleProfiles: StyleProfile[];
  isLoadingTemplates: boolean;
  isLoadingStyleProfiles: boolean;
}

const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  form,
  templates,
  styleProfiles,
  isLoadingTemplates,
  isLoadingStyleProfiles,
}) => {
  return (
    <>
      <FormField
        control={form.control}
        name="templateId"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Content Template</FormLabel>
            <Select onValueChange={field.onChange} value={field.value}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select a content template" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {isLoadingTemplates ? (
                  <div className="px-4 py-2 text-muted-foreground">
                    Loading templates...
                  </div>
                ) : (
                  templates.map((template) => (
                    <SelectItem key={template.id} value={template.id}>
                      {template.name}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
            <FormDescription>
              Choose a pre-defined structure for your content.
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="styleProfileId"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Style Profile</FormLabel>
            <Select onValueChange={field.onChange} value={field.value}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select a style profile" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {isLoadingStyleProfiles ? (
                  <div className="px-4 py-2 text-muted-foreground">
                    Loading styles...
                  </div>
                ) : (
                  styleProfiles
                    .filter(profile => typeof profile.id === "string" && profile.id.trim() !== "")

                    .map((profile) => (
                      <SelectItem key={profile.id} value={profile.id}>
                        {profile.name}
                      </SelectItem>
                    ))
                )}
              </SelectContent>
            </Select>
            <FormDescription>
              Define the tone and style of the generated content.
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    </>
  );
};

export default TemplateSelector;
