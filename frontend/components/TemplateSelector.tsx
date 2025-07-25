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
import { ContentTemplate } from "@/types/content";
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
  isLoadingTemplates: boolean;
}

const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  form,
  templates,
  isLoadingTemplates,
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

  // Helper function to get display name for template
  const getTemplateDisplayName = (template: ContentTemplate): string => {
    // Use title (which comes from your adapter's name -> title mapping)
    const displayName = template.title || template.id;
    return prettyName(displayName);
  };

  // Debug logging
  React.useEffect(() => {
    console.log('TemplateSelector: Rendered with data:', {
      templatesCount: templates?.length || 0,
      validTemplatesCount: validTemplates.length,
      isLoadingTemplates,
      sampleTemplate: validTemplates[0] ? {
        id: validTemplates[0].id,
        title: validTemplates[0].title
      } : null
    });
  }, [templates, validTemplates, isLoadingTemplates]);

  return (
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
  );
};

export default TemplateSelector;