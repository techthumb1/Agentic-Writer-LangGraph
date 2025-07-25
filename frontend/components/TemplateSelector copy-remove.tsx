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
  // Safely filter and validate templates with enhanced checking
  const validTemplates = React.useMemo(() => {
    if (!Array.isArray(templates)) {
      console.warn('TemplateSelector: templates is not an array:', templates);
      return [];
    }
    
    return templates.filter((template): template is ContentTemplate => {
      if (!template || typeof template !== 'object') {
        console.warn('TemplateSelector: Invalid template object:', template);
        return false;
      }
      
      // Check for required fields - using title since your adapter maps name -> title
      const hasId = typeof template.id === 'string' && template.id.length > 0;
      const hasTitle = typeof template.title === 'string' && template.title.length > 0;
      
      if (!hasId) {
        console.warn('TemplateSelector: Template missing ID:', template);
        return false;
      }
      
      if (!hasTitle) {
        console.warn('TemplateSelector: Template missing title:', template);
        return false;
      }
      
      return true;
    });
  }, [templates]);

  // Safely filter and validate style profiles with enhanced checking
  const validStyleProfiles = React.useMemo(() => {
    if (!Array.isArray(styleProfiles)) {
      console.warn('TemplateSelector: styleProfiles is not an array:', styleProfiles);
      return [];
    }
    
    return styleProfiles.filter((profile): profile is StyleProfile => {
      if (!profile || typeof profile !== 'object') {
        console.warn('TemplateSelector: Invalid profile object:', profile);
        return false;
      }
      
      // Check for required fields
      const hasId = typeof profile.id === 'string' && profile.id.length > 0;
      const hasName = typeof profile.name === 'string' && profile.name.length > 0;
      
      if (!hasId) {
        console.warn('TemplateSelector: Profile missing ID:', profile);
        return false;
      }
      
      if (!hasName) {
        console.warn('TemplateSelector: Profile missing name:', profile);
        return false;
      }
      
      return true;
    });
  }, [styleProfiles]);

  // Helper function to get display name for template
  const getTemplateDisplayName = (template: ContentTemplate): string => {
    // Use title (which comes from your adapter's name -> title mapping)
    const displayName = template.title || template.id;
    return prettyName(displayName);
  };

  // Helper function to get display name for style profile
  const getProfileDisplayName = (profile: StyleProfile): string => {
    return profile.name || profile.id;
  };

  // Debug logging
  React.useEffect(() => {
    console.log('TemplateSelector: Rendered with data:', {
      templatesCount: templates?.length || 0,
      validTemplatesCount: validTemplates.length,
      profilesCount: styleProfiles?.length || 0,
      validProfilesCount: validStyleProfiles.length,
      isLoadingTemplates,
      isLoadingStyleProfiles,
      sampleTemplate: validTemplates[0] ? {
        id: validTemplates[0].id,
        title: validTemplates[0].title
      } : null,
      sampleProfile: validStyleProfiles[0] ? {
        id: validStyleProfiles[0].id,
        name: validStyleProfiles[0].name
      } : null
    });
  }, [templates, styleProfiles, validTemplates, validStyleProfiles, isLoadingTemplates, isLoadingStyleProfiles]);

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
                      key={`template-selector-${template.id}`} 
                      value={template.id}
                    >
                      {getTemplateDisplayName(template)}
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
                  validStyleProfiles.map((profile, index) => (
                    <SelectItem 
                      key={`template-selector-profile-${profile.id}-${index}`}
                      value={profile.id}
                    >
                      {getProfileDisplayName(profile)}
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