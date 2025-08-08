// frontend/hooks/useTemplates.ts - Enhanced for Dynamic Template Structure
import { useQuery } from "@tanstack/react-query";
import { ContentTemplate, TemplateParameter } from "@/types/content";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000';

// Enhanced Template Parameter interface
interface EnhancedTemplateParameter extends TemplateParameter {
  commonly_used?: boolean;
  affects_approach?: boolean;
  affects_scope?: boolean;
  affects_tone?: boolean;
  description?: string;
}

// Raw template data structure from API
interface RawTemplateData {
  id: string;
  name?: string;
  title?: string;
  description?: string;
  category?: string;
  difficulty?: string;
  estimatedLength?: string;
  targetAudience?: string;
  icon?: string;
  tags?: string[];
  parameters?: Record<string, unknown> | unknown[];
  templateData?: {
    template_type?: string;
    content_format?: string;
    output_structure?: string;
    generation_mode?: string;
    sections?: unknown[];
    section_order?: string[];
    parameters?: Record<string, unknown> | unknown[];
    original_parameters?: Record<string, unknown>;
    instructions?: string;
    validation_rules?: string[];
    tone?: Record<string, unknown>;
    proposal_specs?: Record<string, unknown>;
    requirements?: Record<string, unknown>;
    quality_targets?: Record<string, unknown>;
    metadata?: Record<string, unknown>;
    filename?: string;
    originalData?: Record<string, unknown>;
  };
  isBuiltIn?: boolean;
  isPublic?: boolean;
  createdBy?: string;
  createdAt?: string | number;
  updatedAt?: string | number;
  suggested_sections?: string[];
  suggested_parameters?: string[];
  instructions?: string;
  metadata?: {
    parameter_flexibility?: string;
    version?: string;
    created_by?: string;
    last_updated?: string;
    template_type?: string;
    content_type?: string;
    template_category?: string;
    [key: string]: unknown;
  };
  system_prompt?: string;
  complexity?: string;
  target_length?: string | { optimal_words?: number; min_words?: number; max_words?: number };
  sections?: unknown[];
  requirements?: Record<string, unknown> | string[];
  quality_targets?: Record<string, unknown> | string[];
  filename?: string;
  template_type?: string;
  content_format?: string;
  output_structure?: string;
  generation_mode?: string;
  section_order?: string[];
  validation_rules?: string[];
  tone?: Record<string, unknown>;
  proposal_specs?: Record<string, unknown>;
}

// API Response interfaces
interface TemplatesAPIResponse {
  templates: RawTemplateData[];
  success: boolean;
}

interface LegacyAPIResponse {
  success: boolean;
  data: {
    items: RawTemplateData[];
  };
}

async function fetcher(url: string): Promise<ContentTemplate[]> {
  console.log('🚀 Fetching templates from:', url);
  
  const res = await fetch(url);
  if (!res.ok) {
    const errorText = await res.text();
    console.error('❌ Templates fetch failed:', res.status, res.statusText, errorText);
    throw new Error(`Failed to fetch templates: ${res.status} ${res.statusText}`);
  }
  
  const result: TemplatesAPIResponse | LegacyAPIResponse | RawTemplateData[] = await res.json();
  
  console.log('🔍 Templates API response structure:', {
    type: typeof result,
    isArray: Array.isArray(result),
    keys: result && typeof result === 'object' ? Object.keys(result) : 'not object',
    hasTemplates: 'templates' in result && result.templates !== undefined,
    hasSuccess: 'success' in result && result.success !== undefined,
    templatesLength: 'templates' in result && Array.isArray(result.templates) ? result.templates.length : undefined,
    resultLength: Array.isArray(result) ? result.length : 'not array'
  });
  
  // Handle enhanced API route format { templates: [...], success: true }
  if (result && typeof result === 'object' && 'templates' in result && Array.isArray(result.templates)) {
    console.log(`✅ Found templates in wrapper object: ${result.templates.length} templates`);
    
    const transformedTemplates = result.templates.map((template: RawTemplateData): ContentTemplate => {
      console.log('🔄 Transforming template:', template.id, {
        hasTemplateData: !!template.templateData,
        templateType: template.templateData?.template_type,
        sectionsCount: template.templateData?.sections?.length || 0,
        parametersCount: Object.keys(template.templateData?.parameters || {}).length
      });

      return {
        // Core fields
        id: template.id,
        title: template.title || template.name || 'Untitled',
        description: template.description || '',
        category: template.category || 'general',
        difficulty: template.difficulty,
        estimatedLength: template.estimatedLength,
        targetAudience: template.targetAudience,
        icon: template.icon,
        tags: template.tags || [],
        
        // Enhanced parameters - ensure they're in the expected format
        parameters: transformTemplateParameters(template.parameters || {}),
        
        // Enhanced template data with all dynamic fields
        templateData: {
          // Core template info
          id: template.id,
          template_type: template.templateData?.template_type || template.template_type || 'standard',
          content_format: template.templateData?.content_format || template.content_format || 'standard',
          output_structure: template.templateData?.output_structure || template.output_structure || 'standard',
          generation_mode: template.templateData?.generation_mode || template.generation_mode || 'standard',
          
          // Sections with dynamic structure
          sections: transformSections(template.templateData?.sections || template.sections || []),
          section_order: template.templateData?.section_order || template.section_order || [],
          
          // Parameters in both formats
          parameters: transformTemplateParameters(template.parameters || {}),
          original_parameters: template.templateData?.original_parameters || template.parameters || {},
          
          // Instructions and requirements
          instructions: template.templateData?.instructions || template.instructions || template.system_prompt || '',
          validation_rules: template.templateData?.validation_rules || template.validation_rules || [],
          
          // Tone and style
          tone: template.templateData?.tone || template.tone || {},
          
          // Template-specific configurations
          proposal_specs: template.templateData?.proposal_specs || template.proposal_specs || {},
          requirements: normalizeToRecord(template.templateData?.requirements || template.requirements || {}),
          quality_targets: normalizeToRecord(template.templateData?.quality_targets || template.quality_targets || {}),
          
          // Metadata
          metadata: template.templateData?.metadata || template.metadata || {},
          filename: template.templateData?.filename || template.filename,
          
          // Keep full original data for advanced use cases
          originalData: normalizeToRecord(template.templateData?.originalData || template),
        },
        
        // System fields
        isBuiltIn: template.isBuiltIn !== false,
        isPublic: template.isPublic !== false,
        createdBy: template.createdBy,
        createdAt: safeParseDate(template.createdAt),
        updatedAt: safeParseDate(template.updatedAt),
        
        // Legacy compatibility
        suggested_sections: normalizeSuggestedSections(template.suggested_sections || []),
        suggested_parameters: normalizeSuggestedParameters(template.suggested_parameters || []).map(param => ({
          ...param,
          description: param.description ?? '',
        })),
        instructions: template.templateData?.instructions || template.instructions || template.system_prompt || '',
        metadata: {
          parameter_flexibility: template.metadata?.parameter_flexibility || 'high',
          version: template.metadata?.version || '2.0.0',
          created_by: template.metadata?.created_by || 'system',
          last_updated: template.metadata?.last_updated || new Date().toISOString(),
          template_type: template.templateData?.template_type || template.template_type || 'standard',
          content_type: template.metadata?.content_type || 'dynamic',
          template_category: template.metadata?.template_category || template.category || 'general',
          ...(template.metadata || {})
        },
      };
    });
    
    console.log(`✅ Successfully transformed ${transformedTemplates.length} enhanced templates`);
    return transformedTemplates;
  }
  
  // Legacy: Check for paginated response structure
  if ('success' in result && result.success && 'data' in result && result.data?.items && Array.isArray(result.data.items)) {
    const templates = result.data.items.map((template: RawTemplateData): ContentTemplate => ({
      id: template.id,
      title: template.name || template.title || 'Untitled',
      description: template.description || '',
      category: template.category || 'general',
      difficulty: template.complexity || template.difficulty,
      estimatedLength: extractEstimatedLength(template),
      targetAudience: template.targetAudience,
      icon: template.icon,
      tags: template.tags || [],
      parameters: transformLegacyParameters(template.parameters || {}),
      templateData: {
        id: template.id,
        template_type: 'legacy',
        content_format: 'standard',
        output_structure: 'standard',
        generation_mode: 'standard',
        sections: transformLegacySections(template.sections || []),
        section_order: [],
        parameters: transformLegacyParameters(template.parameters || {}),
        original_parameters: template.parameters || {},
        instructions: template.system_prompt || '',
        validation_rules: [],
        tone: {},
        proposal_specs: {},
        requirements: normalizeToRecord(template.requirements || {}),
        quality_targets: normalizeToRecord(template.quality_targets || {}),
        metadata: template.metadata || {},
        filename: template.filename,
        originalData: normalizeToRecord(template),
      },
      isBuiltIn: true,
      isPublic: true,
      createdAt: new Date(),
      updatedAt: new Date(),
      suggested_sections: [],
      suggested_parameters: [],
      instructions: template.system_prompt || '',
      metadata: {
        version: template.metadata?.version || '1.0.0',
        created_by: template.metadata?.created_by || 'system',
        last_updated: template.metadata?.last_updated || new Date().toISOString(),
        parameter_flexibility: template.metadata?.parameter_flexibility || 'flexible',
        template_type: 'legacy',
        content_type: 'legacy',
        template_category: template.category || 'general'
      },
    }));
    
    console.log(`✅ Loaded ${templates.length} legacy templates`);
    return templates;
  }
  
  // Fallback: Direct array
  if (Array.isArray(result)) {
    console.log(`✅ Using direct array format: ${result.length} templates`);
    return result.map(transformDirectTemplate);
  }
  
  // Enhanced error logging
  console.error('❌ Templates API error - Full result:', JSON.stringify(result, null, 2));
  console.error('❌ No valid template format found');
  
  throw new Error('Failed to load templates - unexpected response format');
}

// Helper function to safely parse dates
function safeParseDate(dateValue: string | number | undefined): Date {
  if (!dateValue) return new Date();
  
  if (typeof dateValue === 'number') {
    return new Date(dateValue);
  }
  
  if (typeof dateValue === 'string') {
    const parsed = new Date(dateValue);
    return isNaN(parsed.getTime()) ? new Date() : parsed;
  }
  
  return new Date();
}

// Helper function to normalize arrays/records to Record<string, unknown>
function normalizeToRecord(value: unknown): Record<string, unknown> {
  if (!value) return {};
  
  if (Array.isArray(value)) {
    // Convert array to record with index keys
    const record: Record<string, unknown> = {};
    value.forEach((item, index) => {
      record[index.toString()] = item;
    });
    return record;
  }
  
  if (typeof value === 'object') {
    return value as Record<string, unknown>;
  }
  
  return { value };
}

// Helper function to normalize suggested sections
function normalizeSuggestedSections(sections: unknown[]): Array<{ name: string; description: string }> {
  if (!Array.isArray(sections)) return [];
  
  return sections.map((section) => {
    if (typeof section === 'string') {
      return { name: section, description: '' };
    }
    if (section && typeof section === 'object') {
      const sectionObj = section as Record<string, unknown>;
      return {
        name: (sectionObj.name as string) || 'Unknown Section',
        description: typeof sectionObj.description === 'string' ? sectionObj.description : '',
      };
    }
    return { name: 'Unknown Section', description: '' };
  });
}

// Helper function to normalize suggested parameters
function normalizeSuggestedParameters(parameters: unknown[]): Array<{
  name: string;
  type: "number" | "text" | "textarea" | "select" | "checkbox" | "multiselect" | "range" | "date";
  label: string;
  commonly_used: boolean;
  description?: string;
}> {
  if (!Array.isArray(parameters)) return [];
  return parameters.map((param) => {
    if (typeof param === 'string') {
      return {
        name: param,
        type: 'text',
        label: param.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        commonly_used: false,
        description: '',
      };
    }
    if (param && typeof param === 'object') {
      const paramObj = param as Record<string, unknown>;
      const name = (paramObj.name as string) || 'Unknown Parameter';
      // Only allow allowed types, fallback to 'text'
      const allowedTypes = [
        "number", "text", "textarea", "select", "checkbox", "multiselect", "range", "date"
      ] as const;
      let type = (paramObj.type as string) || 'text';
      if (!allowedTypes.includes(type as typeof allowedTypes[number])) {
        type = 'text';
      }
      return {
        name,
        type: type as typeof allowedTypes[number],
        label: (paramObj.label as string) || name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        commonly_used: (paramObj.commonly_used as boolean) || false,
        description: typeof paramObj.description === 'string' ? paramObj.description : '',
      };
    }
    return {
      name: 'Unknown Parameter',
      type: 'text',
      label: 'Unknown Parameter',
      commonly_used: false,
      description: '',
    };
  });
}

// Helper function to transform sections
function transformSections(sections: unknown[]): Array<{
  name: string;
  title: string;
  description: string;
  required: boolean;
  content_type: string;
  specifications: string[];
}> {
  if (!Array.isArray(sections)) {
    return [];
  }

  return sections.map((section, index) => {
    if (typeof section === 'string') {
      return {
        name: section,
        title: section,
        description: `Content for ${section}`,
        required: true,
        content_type: 'standard',
        specifications: [],
      };
    }

    if (section && typeof section === 'object') {
      const sectionObj = section as Record<string, unknown>;
      return {
        name: (sectionObj.name as string) || (sectionObj.title as string) || `section_${index}`,
        title: (sectionObj.title as string) || (sectionObj.name as string) || `Section ${index + 1}`,
        description: (sectionObj.description as string) || '',
        required: (sectionObj.required as boolean) !== false,
        content_type: (sectionObj.content_type as string) || 'standard',
        specifications: Array.isArray(sectionObj.specifications) ? sectionObj.specifications as string[] : [],
      };
    }

    return {
      name: `section_${index}`,
      title: `Section ${index + 1}`,
      description: '',
      required: true,
      content_type: 'standard',
      specifications: [],
    };
  });
}

// Helper function to transform template parameters to expected format
function transformTemplateParameters(parameters: Record<string, unknown> | unknown[]): Record<string, EnhancedTemplateParameter> {
  if (!parameters) {
    return {};
  }

  // If it's already in the correct Record format
  if (!Array.isArray(parameters) && typeof parameters === 'object') {
    const transformed: Record<string, EnhancedTemplateParameter> = {};
    
    Object.entries(parameters).forEach(([key, param]) => {
      if (param && typeof param === 'object') {
        const paramObj = param as Record<string, unknown>;
        transformed[key] = {
          name: key,
          label: (paramObj.label as string) || key,
          type: (paramObj.type as TemplateParameter['type']) || 'text',
          description: paramObj.description as string,
          placeholder: paramObj.placeholder as string,
          default: paramObj.default as string | number | boolean,
          options: paramObj.options as string[] | Record<string, string>,
          required: (paramObj.required as boolean) || false,
          commonly_used: (paramObj.commonly_used as boolean) || false,
          affects_approach: (paramObj.affects_approach as boolean) || false,
          affects_scope: (paramObj.affects_scope as boolean) || false,
          affects_tone: (paramObj.affects_tone as boolean) || false,
          validation: paramObj.validation as TemplateParameter['validation'],
        };
      }
    });
    
    return transformed;
  }

  // If it's an array of parameter objects, transform to Record format
  if (Array.isArray(parameters)) {
    const transformed: Record<string, EnhancedTemplateParameter> = {};
    
    parameters.forEach((param) => {
      if (param && typeof param === 'object') {
        const paramObj = param as Record<string, unknown>;
        const name = paramObj.name as string;
        
        if (name) {
          transformed[name] = {
            name,
            label: (paramObj.label as string) || name,
            type: (paramObj.type as TemplateParameter['type']) || 'text',
            description: paramObj.description as string,
            placeholder: paramObj.placeholder as string,
            default: paramObj.default as string | number | boolean,
            options: paramObj.options as string[] | Record<string, string>,
            required: (paramObj.required as boolean) || false,
            commonly_used: (paramObj.commonly_used as boolean) || false,
            affects_approach: (paramObj.affects_approach as boolean) || false,
            affects_scope: (paramObj.affects_scope as boolean) || false,
            affects_tone: (paramObj.affects_tone as boolean) || false,
            validation: paramObj.validation as TemplateParameter['validation'],
          };
        }
      }
    });

    return transformed;
  }

  return {};
}

// Helper function to transform legacy parameters
function transformLegacyParameters(parameters: Record<string, unknown> | unknown[]): Record<string, EnhancedTemplateParameter> {
  if (!parameters || typeof parameters !== 'object') {
    return {};
  }

  const transformed: Record<string, EnhancedTemplateParameter> = {};
  
  if (Array.isArray(parameters)) {
    parameters.forEach((param) => {
      if (param && typeof param === 'object') {
        const paramObj = param as Record<string, unknown>;
        const name = paramObj.name as string;
        
        if (name) {
          transformed[name] = {
            name,
            label: (paramObj.label as string) || name.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            type: (paramObj.type as TemplateParameter['type']) || 'text',
            description: paramObj.description as string,
            placeholder: paramObj.placeholder as string,
            default: paramObj.default as string | number | boolean,
            options: paramObj.options as string[] | Record<string, string>,
            required: (paramObj.required as boolean) || false,
            commonly_used: false,
            affects_approach: false,
            affects_scope: false,
            affects_tone: false,
          };
        }
      }
    });
  } else {
    Object.entries(parameters).forEach(([key, param]) => {
      if (param && typeof param === 'object') {
        const paramObj = param as Record<string, unknown>;
        transformed[key] = {
          name: key,
          label: (paramObj.label as string) || key.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
          type: (paramObj.type as TemplateParameter['type']) || 'text',
          description: paramObj.description as string,
          placeholder: paramObj.placeholder as string,
          default: paramObj.default as string | number | boolean,
          options: paramObj.options as string[] | Record<string, string>,
          required: (paramObj.required as boolean) || false,
          commonly_used: false,
          affects_approach: false,
          affects_scope: false,
          affects_tone: false,
        };
      }
    });
  }

  return transformed;
}

// Helper function to transform legacy sections
function transformLegacySections(sections: unknown[]): Array<{
  name: string;
  title: string;
  description: string;
  required: boolean;
  content_type: string;
  specifications: string[];
}> {
  if (!Array.isArray(sections)) {
    return [];
  }

  return sections.map((section, index) => {
    if (typeof section === 'string') {
      return {
        name: section,
        title: section,
        description: `Content for ${section}`,
        required: true,
        content_type: 'standard',
        specifications: [],
      };
    }

    if (section && typeof section === 'object') {
      const sectionObj = section as Record<string, unknown>;
      return {
        name: (sectionObj.name as string) || (sectionObj.title as string) || `section_${index}`,
        title: (sectionObj.title as string) || (sectionObj.name as string) || `Section ${index + 1}`,
        description: (sectionObj.description as string) || '',
        required: (sectionObj.required as boolean) !== false,
        content_type: (sectionObj.content_type as string) || 'standard',
        specifications: Array.isArray(sectionObj.specifications) ? sectionObj.specifications as string[] : [],
      };
    }

    return {
      name: `section_${index}`,
      title: `Section ${index + 1}`,
      description: '',
      required: true,
      content_type: 'standard',
      specifications: [],
    };
  });
}

// Helper function to extract estimated length from various formats
function extractEstimatedLength(template: RawTemplateData): string | undefined {
  if (template.estimatedLength) {
    return template.estimatedLength;
  }
  
  if (template.target_length) {
    if (typeof template.target_length === 'object') {
      const tl = template.target_length;
      if (tl.optimal_words) {
        return `${tl.optimal_words} words`;
      }
      if (tl.min_words && tl.max_words) {
        return `${tl.min_words}-${tl.max_words} words`;
      }
    }
    return String(template.target_length);
  }
  
  return undefined;
}

// Helper function to transform direct template array items
function transformDirectTemplate(template: RawTemplateData): ContentTemplate {
  return {
    id: template.id,
    title: template.title || template.name || 'Untitled',
    description: template.description || '',
    category: template.category || 'general',
    difficulty: template.difficulty || template.complexity,
    estimatedLength: extractEstimatedLength(template),
    targetAudience: template.targetAudience,
    icon: template.icon,
    tags: template.tags || [],
    parameters: transformTemplateParameters(template.parameters || {}),
    templateData: {
      id: template.id,
      template_type: template.template_type || 'standard',
      content_format: template.content_format || 'standard',
      output_structure: template.output_structure || 'standard',
      generation_mode: template.generation_mode || 'standard',
      sections: transformSections(template.sections || []),
      section_order: template.section_order || [],
      parameters: transformTemplateParameters(template.parameters || {}),
      original_parameters: template.parameters || {},
      instructions: template.instructions || '',
      validation_rules: template.validation_rules || [],
      tone: template.tone || {},
      proposal_specs: template.proposal_specs || {},
      requirements: normalizeToRecord(template.requirements || {}),
      quality_targets: normalizeToRecord(template.quality_targets || {}),
      metadata: template.metadata || {},
      filename: template.filename,
      originalData: normalizeToRecord(template),
    },
    isBuiltIn: true,
    isPublic: true,
    createdAt: safeParseDate(template.createdAt),
    updatedAt: safeParseDate(template.updatedAt),
    suggested_sections: normalizeSuggestedSections(template.suggested_sections || []),
    suggested_parameters: normalizeSuggestedParameters(template.suggested_parameters || []).map(param => ({
      ...param,
      description: param.description ?? '',
    })),
    instructions: template.instructions || '',
    metadata: {
      version: template.metadata?.version || '2.0.0',
      created_by: template.metadata?.created_by || 'system',
      last_updated: template.metadata?.last_updated || new Date().toISOString(),
      parameter_flexibility: template.metadata?.parameter_flexibility || 'high',
      template_type: template.template_type || 'standard',
      content_type: template.metadata?.content_type || 'dynamic',
      template_category: template.category || 'general',
      ...(template.metadata || {})
    },
  };
}

// Enhanced hook with better error handling and type safety
export function useTemplates() {
  const query = useQuery<ContentTemplate[], Error>({
    queryKey: ['templates'],
    queryFn: async () => {
      console.log('🔄 useTemplates: Starting enhanced fetch...');
      const result = await fetcher(`${BACKEND_URL}/api/templates?page=1&limit=100`);
      
      console.log('🔍 useTemplates: Final enhanced result:', {
        type: typeof result,
        isArray: Array.isArray(result),
        length: Array.isArray(result) ? result.length : 'not array',
        firstItem: Array.isArray(result) && result.length > 0 ? {
          id: result[0].id,
          title: result[0].title,
          templateType: result[0].templateData?.template_type,
          sectionsCount: result[0].templateData?.sections?.length || 0,
          parametersCount: Object.keys(result[0].templateData?.parameters || {}).length
        } : 'none'
      });
      
      return result;
    },
    staleTime: 5 * 60 * 1000,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // Enhanced return interface supporting all component patterns
  return {
    // Standard React Query interface (for page.tsx)
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    
    // Component-expected interface (for TemplateSelector.tsx)
    templates: query.data,
    
    // Additional helpers
    refetch: query.refetch,
    isRefetching: query.isRefetching,
  };
}

export function useTemplate(id: string) {
  const { data: templates, isLoading, error } = useTemplates();
  
  const template = Array.isArray(templates) ? templates.find(t => t.id === id) : undefined;
  
  return {
    data: template,
    isLoading,
    error: template ? null : error,
    refetch: () => {}, // Template-specific refetch would need separate implementation
  };
}

// Helper function to convert enhanced parameters to array format for DynamicParameters
export function getTemplateParametersAsArray(template: ContentTemplate): Array<{
  name: string;
  label?: string;
  type: "text" | "textarea" | "select" | "number" | "checkbox" | "multiselect" | "range" | "date";
  options?: Record<string, string> | string[];
  default?: string | number | boolean;
  required?: boolean;
  placeholder?: string;
  description?: string;
  commonly_used?: boolean;
  affects_approach?: boolean;
  affects_scope?: boolean;
  affects_tone?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
}> {
  if (!template.templateData?.parameters) return [];
  
  return Object.entries(template.templateData.parameters).map(([key, param]) => ({
    name: key,
    label: param.label || key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    type: param.type || 'text',
    options: param.options,
    default: normalizeParameterDefault(param.default, param.type),
    required: param.required || false,
    placeholder: param.placeholder,
    description: param.description,
    commonly_used: param.commonly_used || false,
    affects_approach: param.affects_approach || false,
    affects_scope: param.affects_scope || false,
    affects_tone: param.affects_tone || false,
    validation: param.validation,
  }));
}

// Helper function to normalize parameter default values
function normalizeParameterDefault(
  defaultValue: unknown, 
  type: string
): string | number | boolean | undefined {
  if (defaultValue === undefined || defaultValue === null) {
    return undefined;
  }
  
  // For multiselect, convert arrays to single values or undefined
  if (type === 'multiselect') {
    if (Array.isArray(defaultValue)) {
      return defaultValue.length > 0 ? defaultValue[0] : undefined;
    }
    return defaultValue as string | number | boolean | undefined;
  }
  
  // For other types, ensure single values
  if (Array.isArray(defaultValue)) {
    return defaultValue.length > 0 ? defaultValue[0] : undefined;
  }
  
  return defaultValue as string | number | boolean;
}

// Helper function to get template sections for display
export function getTemplateSections(template: ContentTemplate) {
  return template.templateData?.sections || [];
}

// Helper function to check if template has enhanced features
export function isEnhancedTemplate(template: ContentTemplate): boolean {
  return template.templateData?.template_type !== 'legacy' && 
         template.templateData?.template_type !== 'standard';
}