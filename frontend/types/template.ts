// frontend/types/template.ts - Updated to match current template structure

export interface TemplateParameter {
  label: string;
  type: 'text' | 'textarea' | 'select' | 'number' | 'checkbox' | 'boolean' | 'string';
  description?: string;
  options?: string[];
  required?: boolean;
  placeholder?: string;
  default?: string | number | boolean;
  commonly_used?: boolean;
  min?: number;
  max?: number;

}

export interface Template {
  id: string;
  name: string;
  description: string;
  category?: string;
  difficulty?: string;
  estimatedLength?: string;
  slug?: string;
  filename?: string;
  system_prompt?: string;
  structure?: Record<string, unknown>;
  research?: Record<string, unknown>;
  version?: string;
  defaults?: Record<string, unknown>;

  targetAudience?: string;
  icon?: string;
  tags?: string[];
  complexity?: string;
  recommended_styles?: string[];
  sections?: Array<{
    title?: string;
    name?: string;
    description?: string;
    required?: boolean;
  }>;
  target_length?: {
    min_words?: number;
    max_words?: number;
    optimal_words?: number;
  };
  requirements?: Record<string, boolean>;
  quality_targets?: Record<string, number>;
  parameters?: Record<string, TemplateParameter>;
  suggested_sections?: Array<{
    name: string;
    description: string;
  }>;
  instructions?: string;
  metadata?: Record<string, unknown>;
}

export interface TemplateCollection {
  templates: Template[];
  total: number;
  page?: number;
  limit?: number;
}

export interface TemplateFormData {
  templateId: string;
  parameters: Record<string, string | number | boolean>;
}

// Type guards for runtime validation
export function isTemplate(obj: unknown): obj is Template {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj &&
    typeof (obj as Template).id === 'string' &&
    typeof (obj as Template).name === 'string'
  );
}

export function isTemplateParameter(obj: unknown): obj is TemplateParameter {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'type' in obj &&
    'label' in obj &&
    typeof (obj as TemplateParameter).type === 'string' &&
    typeof (obj as TemplateParameter).label === 'string'
  );
}

export function hasParameters(template: Template): boolean {
  return !!(
    template.parameters &&
    typeof template.parameters === 'object' &&
    Object.keys(template.parameters).length > 0
  );
}

// Helper function to get parameter defaults
export function getParameterDefaults(template: Template): Record<string, string | number | boolean> {
  if (!template.parameters) return {};
  
  const defaults: Record<string, string | number | boolean> = {};
  
  Object.entries(template.parameters).forEach(([key, param]) => {
    if (param.default !== undefined) {
      defaults[key] = param.default;
    } else {
      // Set sensible defaults based on type
      switch (param.type) {
        case 'text':
        case 'textarea':
        case 'select':
        case 'string':
          defaults[key] = '';
          break;
        case 'number':
          defaults[key] = 0;
          break;
        case 'checkbox':
        case 'boolean':
          defaults[key] = false;
          break;
        default:
          defaults[key] = '';
      }
    }
  });
  
  return defaults;
}

// Helper to get commonly used parameters
export function getCommonlyUsedParameters(template: Template): Record<string, TemplateParameter> {
  if (!template.parameters) return {};
  
  const commonParams: Record<string, TemplateParameter> = {};
  
  Object.entries(template.parameters).forEach(([key, param]) => {
    if (param.commonly_used) {
      commonParams[key] = param;
    }
  });
  
  return commonParams;
}

// Helper to validate parameter values
export function validateParameterValue(
  param: TemplateParameter,
  value: string | number | boolean
): boolean {
  if (param.required && (value === '' || value === null || value === undefined)) {
    return false;
  }
  
  if (param.type === 'number' && typeof value === 'string') {
    return !isNaN(Number(value));
  }
  
  if (param.type === 'select' && param.options && typeof value === 'string') {
    return param.options.includes(value);
  }
  
  return true;
}