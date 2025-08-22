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

// V2 Template types
interface V2TemplateInput {
  default?: unknown;
  required?: boolean;
  enum?: unknown[];
}

interface V2MCPConfig {
  [key: string]: unknown;
}

interface V2TemplateParameter {
  key: string;
  label: string;
  required: boolean;
  default: unknown;
  type: "string" | "number" | "boolean" | "enum";
  options?: unknown;
}

interface V2NormalizedTemplate {
  id: string;
  name: string;
  slug?: string;
  description?: string;
  parameters: V2TemplateParameter[];
  original_parameters: V2TemplateParameter[];
  inputs: Record<string, V2TemplateInput>;
  requirements?: unknown;
  writer_instructions?: string;
  mcp?: V2MCPConfig;
  sections?: unknown;
  section_order: string[];
  metadata?: unknown;
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
  // V2 Template fields
  inputs?: Record<string, V2TemplateInput>;
  writer_instructions?: string;
  mcp?: V2MCPConfig;
  slug?: string;
}

// Remove unused interfaces
// These interfaces are no longer needed since we handle API responses dynamically

// Converts template v2 { inputs: {...} } to the UI-friendly { parameters: [...] }
export function normalizeTemplateV2ToUI(t: RawTemplateData): V2NormalizedTemplate {
  const inferType = (v: unknown): "string" | "number" | "boolean" | "enum" => {
    if (Array.isArray(v)) return "enum";
    switch (typeof v) {
      case "number": return "number";
      case "boolean": return "boolean";
      default: return "string";
    }
  };

  const sections = t?.sections;
  const inputs = (t?.inputs && typeof t.inputs === "object") ? t.inputs : {};
  const parameters = Object.entries(inputs).map(([key, spec]: [string, V2TemplateInput]) => {
    const label = key
      .replace(/[_\-]+/g, " ")
      .replace(/\b\w/g, (m) => m.toUpperCase());
    const def = spec?.default ?? "";
    const type = inferType(def);
    const options = Array.isArray(spec?.enum) ? spec.enum : undefined;

    return {
      key,
      label,
      required: !!spec?.required,
      default: def,
      type: options ? "enum" : type,
      options
    };
  });

  // Back-compat: expose both .parameters and .original_parameters for existing components
  const normalized: V2NormalizedTemplate = {
    id: t?.id || t?.slug || t?.name || "template",
    name: t?.name || "Template",
    slug: t?.slug,
    description: t?.description,
    // UI expects .parameters; keep original for legacy code paths
    parameters,
    original_parameters: parameters,

    // expose raw v2 for advanced UIs
    inputs,
    requirements: t?.requirements,
    writer_instructions: t?.writer_instructions,
    mcp: t?.mcp,
    sections: t?.sections,
    section_order: Array.isArray(sections) && 'order' in (sections as unknown as Record<string, unknown>) && Array.isArray((sections as unknown as Record<string, unknown>).order) 
      ? ((sections as unknown as Record<string, unknown>).order as unknown[]).map(item => String(item))
      : // handle priority array: pick the first array found
      (() => {
        const sectionsObj = sections as unknown as Record<string, unknown> | undefined;
        const pr = sectionsObj?.order as Record<string, unknown> | undefined;
        const priority = pr?.priority;
        if (Array.isArray(priority)) {
          for (const candidate of priority) {
            if (candidate && typeof candidate !== "string" && Array.isArray(candidate)) {
              return candidate.map(item => String(item));
            }
          }
        }
        return [];
      })(),
    metadata: t?.metadata,
  };

  return normalized;
}

// Remove the unused fetcher function completely

// Helper function to transform V2 parameters to Record format
function transformV2ParametersToRecord(parameters: V2TemplateParameter[]): Record<string, EnhancedTemplateParameter> {
  if (!Array.isArray(parameters)) return {};
  
  const transformed: Record<string, EnhancedTemplateParameter> = {};
  
  parameters.forEach((param) => {
    if (param && param.key) {
      transformed[param.key] = {
        name: param.key,
        label: param.label || param.key,
        type: mapV2TypeToTemplateType(param.type),
        description: '',
        placeholder: '',
        default: param.default as string | number | boolean,
        options: param.options as string[] | Record<string, string>,
        required: param.required || false,
        commonly_used: false,
        affects_approach: false,
        affects_scope: false,
        affects_tone: false,
      };
    }
  });
  
  return transformed;
}

// Helper function to map V2 types to template types
function mapV2TypeToTemplateType(v2Type: string): TemplateParameter['type'] {
  switch (v2Type) {
    case 'enum': return 'select';
    case 'string': return 'text';
    case 'number': return 'number';
    case 'boolean': return 'checkbox';
    default: return 'text';
  }
}

// Helper function to transform V2 sections
function transformV2Sections(sections: unknown): Array<{
  name: string;
  title: string;
  description: string;
  required: boolean;
  content_type: string;
  specifications: string[];
}> {
  if (!Array.isArray(sections)) return [];
  
  return sections.map((section, index) => {
    if (typeof section === 'string') {
      return {
        name: section,
        title: section,
        description: `V2 Content for ${section}`,
        required: true,
        content_type: 'v2_dynamic',
        specifications: [],
      };
    }
    
    if (section && typeof section === 'object') {
      const sectionObj = section as Record<string, unknown>;
      return {
        name: (sectionObj.name as string) || (sectionObj.title as string) || `v2_section_${index}`,
        title: (sectionObj.title as string) || (sectionObj.name as string) || `V2 Section ${index + 1}`,
        description: (sectionObj.description as string) || '',
        required: (sectionObj.required as boolean) !== false,
        content_type: 'v2_dynamic',
        specifications: Array.isArray(sectionObj.specifications) ? sectionObj.specifications as string[] : [],
      };
    }
    
    return {
      name: `v2_section_${index}`,
      title: `V2 Section ${index + 1}`,
      description: '',
      required: true,
      content_type: 'v2_dynamic',
      specifications: [],
    };
  });
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

// Remove unused legacy transformation functions since we only handle V2 templates now

// Remove unused legacy sections transformation

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
  // Check if this is a V2 template and apply normalization
  if (template.inputs) {
    const normalizedV2 = normalizeTemplateV2ToUI(template);
    
    return {
      id: normalizedV2.id,
      title: normalizedV2.name || template.title || template.name || 'Untitled',
      description: normalizedV2.description || template.description || '',
      category: template.category || 'general',
      difficulty: template.difficulty || template.complexity,
      estimatedLength: extractEstimatedLength(template),
      targetAudience: template.targetAudience,
      icon: template.icon,
      tags: template.tags || [],
      parameters: transformV2ParametersToRecord(normalizedV2.parameters),
      templateData: {
        id: normalizedV2.id,
        template_type: 'v2_direct',
        content_format: 'v2_enhanced',
        output_structure: 'v2_dynamic',
        generation_mode: 'v2_intelligent',
        sections: transformV2Sections(normalizedV2.sections || []),
        section_order: Array.isArray(normalizedV2.section_order) ? normalizedV2.section_order.map(item => String(item)) : [],
        parameters: transformV2ParametersToRecord(normalizedV2.parameters),
        original_parameters: normalizedV2.original_parameters || {},
        instructions: normalizedV2.writer_instructions || template.instructions || '',
        validation_rules: [],
        tone: {},
        proposal_specs: {},
        requirements: normalizeToRecord(normalizedV2.requirements || {}),
        quality_targets: {},
        metadata: {
          ...(typeof normalizedV2.metadata === 'object' && normalizedV2.metadata !== null ? normalizedV2.metadata as Record<string, unknown> : {}),
          v2_template: true,
          inputs: normalizedV2.inputs,
          mcp: normalizedV2.mcp
        },
        filename: template.filename,
        originalData: normalizeToRecord(template),
      },
      isBuiltIn: true,
      isPublic: true,
      createdAt: safeParseDate(template.createdAt),
      updatedAt: safeParseDate(template.updatedAt),
      suggested_sections: normalizeSuggestedSections(Array.isArray(normalizedV2.sections) ? normalizedV2.sections : []),
      suggested_parameters: normalizedV2.parameters.map((param: V2TemplateParameter) => ({
        name: param.key,
        type: mapV2TypeToTemplateType(param.type),
        label: param.label,
        commonly_used: false,
        description: '',
      })),
      instructions: normalizedV2.writer_instructions || template.instructions || '',
      metadata: {
        version: '2.0.0',
        created_by: 'system',
        last_updated: new Date().toISOString(),
        parameter_flexibility: 'high',
        template_type: 'v2_direct',
        content_type: 'v2_dynamic',
        template_category: template.category || 'general',
        v2_template: true,
      },
    };
  }

  // Original transformation for non-V2 templates
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

export function useTemplates() {
  return useQuery<ContentTemplate[], Error>({
    queryKey: ['templates'],
    queryFn: async (): Promise<ContentTemplate[]> => {
      console.log('📄 useTemplates: Starting enhanced fetch...');
      // Keep your current fetch path
      const res = await fetch(`${BACKEND_URL}/api/templates?page=1&limit=100`);
      if (!res.ok) throw new Error(`Failed to load templates: ${res.status}`);
      const data = await res.json();

      console.log('🔍 Raw API response:', data);

      // Handle different response formats more robustly
      let items: RawTemplateData[] = [];
      
      if (Array.isArray(data)) {
        // Direct array response
        items = data;
      } else if (data && typeof data === 'object') {
        // Check for different nested structures
        if (Array.isArray(data.templates)) {
          items = data.templates;
        } else if (Array.isArray(data.items)) {
          items = data.items;
        } else if (data.data && Array.isArray(data.data.items)) {
          items = data.data.items;
        } else if (data.data && Array.isArray(data.data)) {
          items = data.data;
        } else {
          console.error('❌ Unexpected API response structure:', data);
          throw new Error('API response does not contain a valid templates array');
        }
      } else {
        console.error('❌ Invalid API response type:', typeof data);
        throw new Error('Invalid API response format');
      }

      console.log('📋 Extracted items:', {
        count: items.length,
        isArray: Array.isArray(items),
        firstItem: items.length > 0 ? {
          id: items[0]?.id,
          name: items[0]?.name,
          hasInputs: !!items[0]?.inputs
        } : null
      });

      if (!Array.isArray(items)) {
        console.error('❌ Items is not an array:', items);
        throw new Error('Failed to extract templates array from API response');
      }
      
      // Transform items to ContentTemplate format
      const result: ContentTemplate[] = items.map((t: RawTemplateData) => {
        if (t.inputs) {
          // Handle V2 templates
          const normalizedV2 = normalizeTemplateV2ToUI(t);
          return {
            id: normalizedV2.id,
            title: normalizedV2.name,
            description: normalizedV2.description || '',
            category: 'general',
            difficulty: undefined,
            estimatedLength: undefined,
            targetAudience: undefined,
            icon: undefined,
            tags: [],
            parameters: transformV2ParametersToRecord(normalizedV2.parameters),
            templateData: {
              id: normalizedV2.id,
              template_type: 'v2',
              content_format: 'v2_enhanced',
              output_structure: 'v2_dynamic',
              generation_mode: 'v2_intelligent',
              sections: transformV2Sections(normalizedV2.sections),
              section_order: Array.isArray(normalizedV2.section_order) ? normalizedV2.section_order.map(item => String(item)) : [],
              parameters: transformV2ParametersToRecord(normalizedV2.parameters),
              original_parameters: normalizeToRecord(normalizedV2.original_parameters),
              instructions: normalizedV2.writer_instructions || '',
              validation_rules: [],
              tone: {},
              proposal_specs: {},
              requirements: normalizeToRecord(normalizedV2.requirements),
              quality_targets: {},
              metadata: {
                ...(typeof normalizedV2.metadata === 'object' && normalizedV2.metadata !== null ? normalizedV2.metadata as Record<string, unknown> : {}),
                v2_template: true,
                inputs: normalizedV2.inputs,
                mcp: normalizedV2.mcp
              },
              filename: undefined,
              originalData: normalizeToRecord(t),
            },
            isBuiltIn: true,
            isPublic: true,
            createdBy: undefined,
            createdAt: new Date(),
            updatedAt: new Date(),
            suggested_sections: normalizeSuggestedSections(Array.isArray(normalizedV2.sections) ? normalizedV2.sections : []),
            suggested_parameters: normalizedV2.parameters.map((param: V2TemplateParameter) => ({
              name: param.key,
              type: mapV2TypeToTemplateType(param.type),
              label: param.label,
              commonly_used: false,
              description: '',
            })),
            instructions: normalizedV2.writer_instructions || '',
            metadata: {
              parameter_flexibility: 'high',
              version: '2.0.0',
              created_by: 'system',
              last_updated: new Date().toISOString(),
              template_type: 'v2',
              content_type: 'v2_dynamic',
              template_category: 'general',
              v2_template: true,
            },
          };
        } else {
          // Handle legacy templates - use existing fetcher logic
          return transformDirectTemplate(t);
        }
      });
      
      console.log('🔍 useTemplates: Final enhanced result:', {
        type: typeof result,
        isArray: Array.isArray(result),
        length: Array.isArray(result) ? result.length : 'not array',
        firstItem: Array.isArray(result) && result.length > 0 ? {
          id: result[0].id,
          title: result[0].title,
          hasV2Template: result[0].metadata?.v2_template,
          parametersCount: Object.keys(result[0].templateData?.parameters || {}).length
        } : 'none'
      });
      
      return result;
    },
    staleTime: 5 * 60 * 1000,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
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