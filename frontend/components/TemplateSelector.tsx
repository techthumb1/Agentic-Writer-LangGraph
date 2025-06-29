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
  // Safely filter and validate templates
  const validTemplates = React.useMemo(() => {
    if (!Array.isArray(templates)) return [];
    
    return templates.filter((template): template is ContentTemplate => {
      return (
        template &&
        typeof template === 'object' &&
        typeof template.id === 'string' &&
        template.id.length > 0
      );
    });
  }, [templates]);

  // Safely filter and validate style profiles
  const validStyleProfiles = React.useMemo(() => {
    if (!Array.isArray(styleProfiles)) return [];
    
    return styleProfiles.filter((profile): profile is StyleProfile => {
      return (
        profile &&
        typeof profile === 'object' &&
        typeof profile.id === 'string' &&
        profile.id.length > 0 &&
        !!(profile.name || profile.id)
      );
    });
  }, [styleProfiles]);

  return (
    <>
      <FormField
        control={form.control}
        name="templateId"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Content Template</FormLabel>
            <Select 
              onValueChange={field.onChange} 
              value={field.value || ""}
              disabled={isLoadingTemplates}
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select a content template" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {isLoadingTemplates ? (
                  <div key="loading-templates" className="px-4 py-2 text-muted-foreground">
                    Loading templates...
                  </div>
                ) : validTemplates.length > 0 ? (
                  validTemplates.map((template) => (
                    <SelectItem 
                      key={`template-${template.id}`} 
                      value={template.id}
                    >
                      {prettyName(template.title || template.id)}
                    </SelectItem>
                  ))
                ) : (
                  <div key="no-templates" className="px-4 py-2 text-red-500">
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
        name="styleProfileId"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Style Profile</FormLabel>
            <Select 
              onValueChange={field.onChange} 
              value={field.value || ""}
              disabled={isLoadingStyleProfiles}
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select a style profile" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {isLoadingStyleProfiles ? (
                  <div key="loading-profiles" className="px-4 py-2 text-muted-foreground">
                    Loading styles...
                  </div>
                ) : validStyleProfiles.length > 0 ? (
                  validStyleProfiles.map((profile) => (
                    <SelectItem 
                      key={`profile-${profile.id}`} 
                      value={profile.id}
                    >
                      {profile.name || profile.id}
                    </SelectItem>
                  ))
                ) : (
                  <div key="no-profiles" className="px-4 py-2 text-red-500">
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