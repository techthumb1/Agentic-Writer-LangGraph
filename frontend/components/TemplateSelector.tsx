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
import { Badge } from "@/components/ui/badge";
import { ContentTemplate } from "@/types/content";
import { UseFormReturn } from "react-hook-form";
import { prettyName } from "@/lib/string";
import { FileText, Clock, Users, Zap, Star } from "lucide-react";

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
  // Get selected template for preview
  const selectedTemplateId = form.watch("templateId");
  const selectedTemplate = templates.find(t => t.id === selectedTemplateId);

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

  // Helper function to get template category badge color
  const getCategoryBadgeVariant = (category: string) => {
    switch (category.toLowerCase()) {
      case 'business':
        return 'default';
      case 'technical':
      case 'technical_documentation':
        return 'secondary';
      case 'marketing':
        return 'outline';
      case 'educational':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  // Helper function to get template complexity icon
  const getComplexityIcon = (difficulty?: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':
      case 'easy':
        return <Star className="h-3 w-3 text-green-500" />;
      case 'intermediate':
        return <Zap className="h-3 w-3 text-yellow-500" />;
      case 'advanced':
      case 'expert':
        return <Zap className="h-3 w-3 text-red-500" />;
      default:
        return <FileText className="h-3 w-3 text-gray-500" />;
    }
  };

  // Debug logging
  React.useEffect(() => {
    console.log('TemplateSelector: Rendered with data:', {
      templatesCount: templates?.length || 0,
      validTemplatesCount: validTemplates.length,
      isLoadingTemplates,
      sampleTemplate: validTemplates[0] ? {
        id: validTemplates[0].id,
        title: validTemplates[0].title,
        templateData: validTemplates[0].templateData ? {
          template_type: validTemplates[0].templateData.template_type,
          sectionsCount: validTemplates[0].templateData.sections?.length || 0,
          parametersCount: Object.keys(validTemplates[0].templateData.parameters || {}).length
        } : null
      } : null
    });
  }, [templates, validTemplates, isLoadingTemplates]);

  return (
    <div className="space-y-4">
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
                      className="cursor-pointer"
                    >
                      <div className="flex items-center justify-between w-full">
                        <div className="flex items-center gap-2">
                          {getComplexityIcon(template.difficulty)}
                          <span>{getTemplateDisplayName(template)}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          {template.category && (
                            <Badge 
                              variant={getCategoryBadgeVariant(template.category)}
                              className="text-xs"
                            >
                              {template.category}
                            </Badge>
                          )}
                          {template.templateData?.template_type && 
                           template.templateData.template_type !== 'standard' && (
                            <Badge variant="outline" className="text-xs">
                              {template.templateData.template_type}
                            </Badge>
                          )}
                        </div>
                      </div>
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

      {/* Enhanced Template Preview */}
      {selectedTemplate && (
        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border">
          <div className="space-y-3">
            {/* Template Header */}
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-medium text-sm">
                    {getTemplateDisplayName(selectedTemplate)}
                  </h4>
                  {selectedTemplate.templateData?.template_type && (
                    <Badge variant="secondary" className="text-xs">
                      {selectedTemplate.templateData.template_type}
                    </Badge>
                  )}
                </div>
                {selectedTemplate.description && (
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {selectedTemplate.description}
                  </p>
                )}
              </div>
              
              <div className="flex items-center gap-2">
                {selectedTemplate.difficulty && (
                  <Badge variant="outline" className="text-xs">
                    {selectedTemplate.difficulty}
                  </Badge>
                )}
                {selectedTemplate.category && (
                  <Badge 
                    variant={getCategoryBadgeVariant(selectedTemplate.category)}
                    className="text-xs"
                  >
                    {selectedTemplate.category}
                  </Badge>
                )}
              </div>
            </div>

            {/* Template Metadata */}
            <div className="flex items-center gap-4 text-xs text-gray-500">
              {selectedTemplate.estimatedLength && (
                <div className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  <span>{selectedTemplate.estimatedLength}</span>
                </div>
              )}
              
              {selectedTemplate.targetAudience && (
                <div className="flex items-center gap-1">
                  <Users className="h-3 w-3" />
                  <span>{selectedTemplate.targetAudience}</span>
                </div>
              )}

              {selectedTemplate.templateData?.sections && (
                <div className="flex items-center gap-1">
                  <FileText className="h-3 w-3" />
                  <span>{selectedTemplate.templateData.sections.length} sections</span>
                </div>
              )}

              {selectedTemplate.templateData?.parameters && (
                <div className="flex items-center gap-1">
                  <Zap className="h-3 w-3" />
                  <span>{Object.keys(selectedTemplate.templateData.parameters).length} parameters</span>
                </div>
              )}
            </div>

            {/* Template Tags */}
            {selectedTemplate.tags && selectedTemplate.tags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {selectedTemplate.tags.slice(0, 5).map((tag, index) => (
                  <Badge key={index} variant="outline" className="text-xs px-2 py-0">
                    {tag}
                  </Badge>
                ))}
                {selectedTemplate.tags.length > 5 && (
                  <Badge variant="outline" className="text-xs px-2 py-0">
                    +{selectedTemplate.tags.length - 5} more
                  </Badge>
                )}
              </div>
            )}

            {/* Template Sections Preview */}
            {selectedTemplate.templateData?.sections && 
             selectedTemplate.templateData.sections.length > 0 && (
              <div className="space-y-2">
                <h5 className="text-xs font-medium text-gray-700 dark:text-gray-300">
                  Content Sections:
                </h5>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {selectedTemplate.templateData.sections.slice(0, 6).map((section, index) => (
                    <div key={index} className="text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800 px-2 py-1 rounded border">
                      {section.title || section.name || `Section ${index + 1}`}
                      {section.required && (
                        <span className="text-red-500 ml-1">*</span>
                      )}
                    </div>
                  ))}
                  {selectedTemplate.templateData.sections.length > 6 && (
                    <div className="text-xs text-gray-500 px-2 py-1">
                      +{selectedTemplate.templateData.sections.length - 6} more
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Template Instructions Preview */}
            {selectedTemplate.templateData?.instructions && (
              <div className="space-y-1">
                <h5 className="text-xs font-medium text-gray-700 dark:text-gray-300">
                  Template Instructions:
                </h5>
                <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
                  {selectedTemplate.templateData.instructions.slice(0, 150)}
                  {selectedTemplate.templateData.instructions.length > 150 && '...'}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateSelector;