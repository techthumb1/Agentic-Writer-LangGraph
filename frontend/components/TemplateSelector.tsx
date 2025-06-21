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
import { prettyName } from "@/lib/string";

// Updated interface to match your backend field names
interface GenerateContentFormValues {
  templateId: string;
  styleProfileId: string;
  dynamic_parameters: Record<string, string | number | boolean>;
  platform: string;
  use_mock: boolean;
}

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
        name="templateId" // Changed from "template" to "templateId"
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
                ) : Array.isArray(templates) && templates.length > 0 ? (
                  templates
                    .filter(
                      (template): template is ContentTemplate =>
                        !!template?.id &&
                        typeof template.id === "string" &&
                        !!template.name
                    )
                    .map((template) => (
                    <SelectItem key={template.id} value={template.id}>
                      {prettyName(template.name ?? template.id)}
                    </SelectItem>
                    ))
                ) : (
                  <div className="px-4 py-2 text-red-500">
                    No templates available
                  </div>
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
        name="styleProfileId" // Changed from "style_profile" to "styleProfileId"
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
                ) : Array.isArray(styleProfiles) && styleProfiles.length > 0 ? (
                  styleProfiles
                    .filter(
                      (profile): profile is StyleProfile =>
                        !!profile?.id &&
                        typeof profile.id === "string" &&
                        !!profile.name
                    )
                    .map((profile) => (
                      <SelectItem key={profile.id} value={profile.id}>
                        {profile.name}
                      </SelectItem>
                    ))
                ) : (
                  <div className="px-4 py-2 text-red-500">
                    No style profiles available
                  </div>
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