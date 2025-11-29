// File: frontend/utils/typeAdapters.ts
import type { ContentTemplate, StyleProfile, TemplateParameter, TemplateSection } from '@/types/content';

interface RawYAMLTemplate {
  id: string;
  name: string;
  description?: string;
  category?: string;
  difficulty?: string;
  estimatedLength?: string;
  targetAudience?: string;
  icon?: string;
  tags?: string[];
  complexity?: string;
  parameters?: ParameterArrayItem[];
  suggested_sections?: Array<{
    name: string;
    description: string;
  }>;
  instructions?: string;
  metadata?: Record<string, unknown>;
}

interface BackendTemplate {
  id: string;
  slug?: string;
  name: string;
  description?: string;
  category?: string;
  sections?: unknown[];
  defaults?: Record<string, unknown>;
  system_prompt?: string;
  structure?: Record<string, unknown>;
  research?: Record<string, unknown>;
  parameters?: Record<string, TemplateParameter> | ParameterArrayItem[];
  metadata?: {
    version: string;
    created_by: string;
    last_updated: string;
    parameter_flexibility: string;
  };
  version?: string;
  filename?: string;
}

interface ExtendedStyleProfile {
  id: string;
  name: string;
  description?: string;
  category?: string;
  metadata?: Record<string, unknown>;
}

interface ParameterArrayItem {
  name: string;
  type: string;
  label: string;
  description?: string;
  options?: string[] | Record<string, string>;
  commonly_used?: boolean;
  required?: boolean;
  placeholder?: string;
  default?: string | number | boolean | string[];
}

function safeGet<T>(obj: unknown, path: string, defaultValue: T): T {
  if (!obj || typeof obj !== 'object') return defaultValue;
  
  const keys = path.split('.');
  let current: unknown = obj;
  
  for (const key of keys) {
    if (current && typeof current === 'object' && current !== null && key in current) {
      current = (current as Record<string, unknown>)[key];
    } else {
      return defaultValue;
    }
  }
  
  return current !== undefined ? (current as T) : defaultValue;
}

function validateParameterType(type: string): "text" | "textarea" | "number" | "select" | "checkbox" | "multiselect" | "range" | "date" {
  const validTypes = ["text", "textarea", "number", "select", "checkbox", "multiselect", "range", "date"] as const;
  if (type === "string") return "text";
  if (type === "boolean") return "checkbox";
  return validTypes.includes(type as typeof validTypes[number]) ? type as typeof validTypes[number] : "text";
}

function normalizeOptions(options?: string[] | Record<string, string>): string[] | undefined {
  if (!options) return undefined;
  if (Array.isArray(options)) return options;
  if (typeof options === 'object') return Object.values(options);
  return undefined;
}

function convertParametersArrayToObject(parametersArray?: ParameterArrayItem[]): Record<string, TemplateParameter> {
  if (!parametersArray || !Array.isArray(parametersArray)) return {};

  const parametersObject: Record<string, TemplateParameter> = {};

  parametersArray.forEach(param => {
    if (!param.name) return;

    let defaultValue: string | number | boolean | undefined = undefined;
    if (param.default !== undefined) {
      if (Array.isArray(param.default)) {
        defaultValue = param.default.length > 0 ? param.default[0] : undefined;
      } else {
        defaultValue = param.default;
      }
    }

    parametersObject[param.name] = {
      name: param.name,
      label: param.label || param.name,
      type: validateParameterType(param.type),
      options: normalizeOptions(param.options),
      required: param.required ?? false,
      placeholder: param.placeholder,
      default: defaultValue,
    };
  });

  return parametersObject;
}

export function adaptBackendTemplate(backendTemplate: BackendTemplate | RawYAMLTemplate): ContentTemplate {
  if (!backendTemplate || typeof backendTemplate !== 'object') {
    throw new Error('Invalid backend template: not an object');
  }
  
  const id = safeGet(backendTemplate, 'id', '');
  const name = safeGet(backendTemplate, 'name', '');
  
  if (!id || !name) {
    throw new Error(`Invalid backend template: missing required fields - id: ${id}, name: ${name}`);
  }

  let parametersObject: Record<string, TemplateParameter> = {};
  
  if (backendTemplate.parameters) {
    if (Array.isArray(backendTemplate.parameters)) {
      parametersObject = convertParametersArrayToObject(backendTemplate.parameters);
    } else if (typeof backendTemplate.parameters === 'object') {
      parametersObject = backendTemplate.parameters as Record<string, TemplateParameter>;
    }
  }

  return {
    id,
    title: name,
    description: safeGet(backendTemplate, 'description', ''),
    category: safeGet(backendTemplate, 'category', 'general'),
    difficulty: safeGet(backendTemplate, 'difficulty', undefined),
    estimatedLength: safeGet(backendTemplate, 'estimatedLength', undefined),
    targetAudience: safeGet(backendTemplate, 'targetAudience', undefined),
    icon: safeGet(backendTemplate, 'icon', undefined),
    tags: safeGet(backendTemplate, 'tags', []),
    parameters: parametersObject,
    templateData: {
      id,
      template_type: 'standard',
      content_format: 'standard',
      output_structure: 'standard',
      generation_mode: 'standard',
      sections: safeGet(backendTemplate, 'sections', []) as TemplateSection[],
      section_order: [],
      parameters: parametersObject,
      original_parameters: backendTemplate.parameters,
      instructions: safeGet(backendTemplate, 'instructions', ''),
      validation_rules: [],
      tone: {},
      proposal_specs: {},
      requirements: {},
      quality_targets: {},
      metadata: safeGet(backendTemplate, 'metadata', {}),
      filename: safeGet(backendTemplate, 'filename', undefined),
      originalData: backendTemplate as unknown as Record<string, unknown>,
    },
    instructions: safeGet(backendTemplate, 'instructions', ''),
    metadata: {
      ...safeGet(backendTemplate, 'metadata', {}),
      parameter_flexibility: safeGet(backendTemplate, 'metadata.parameter_flexibility', 'default'),
    },
    isBuiltIn: true,
    isPublic: true,
    createdAt: new Date(),
    updatedAt: new Date(),
  };
}

export function adaptExtendedStyleProfile(extendedProfile: ExtendedStyleProfile): StyleProfile {
  if (!extendedProfile || typeof extendedProfile !== 'object') {
    throw new Error('Invalid extended profile: not an object');
  }
  
  const id = safeGet(extendedProfile, 'id', '');
  const name = safeGet(extendedProfile, 'name', '');
  
  if (!id || !name) {
    throw new Error(`Invalid extended profile: missing required fields - id: ${id}, name: ${name}`);
  }

  return {
    id,
    name,
    description: safeGet(extendedProfile, 'description', `Style profile: ${name}`),
    category: safeGet(extendedProfile, 'category', 'general'),
    icon: undefined,
    tags: [],
    profileData: {
      metadata: safeGet(extendedProfile, 'metadata', {}),
    },
    isBuiltIn: true,
    isPublic: true,
    createdAt: new Date(),
    updatedAt: new Date(),
  };
}

export function adaptTemplateCollection(backendTemplates: unknown): ContentTemplate[] {
  if (!backendTemplates) return [];

  let templatesArray: unknown[] = [];
  
  if (Array.isArray(backendTemplates)) {
    templatesArray = backendTemplates;
  } else if (typeof backendTemplates === 'object' && backendTemplates !== null) {
    const response = backendTemplates as Record<string, unknown>;
    
    if (Array.isArray(response.templates)) {
      templatesArray = response.templates;
    } else if (response.data) {
      if (Array.isArray((response.data as Record<string, unknown>)?.items)) {
        templatesArray = (response.data as Record<string, unknown>).items as unknown[];
      } else if (Array.isArray(response.data)) {
        templatesArray = response.data as unknown[];
      }
    } else if (Array.isArray(response.results)) {
      templatesArray = response.results;
    } else if (Array.isArray(response.items)) {
      templatesArray = response.items;
    } else {
      return [];
    }
  } else {
    return [];
  }

  const results: ContentTemplate[] = [];
  
  for (let i = 0; i < templatesArray.length; i++) {
    const template = templatesArray[i];
    
    try {
      const templateObj = template as Record<string, unknown>;
      const hasObjectParameters = templateObj && typeof templateObj === 'object' && 
        templateObj.parameters && typeof templateObj.parameters === 'object' && !Array.isArray(templateObj.parameters);
      
      if (hasObjectParameters) {
        const backendTemplate = template as BackendTemplate;
        const parametersArray: ParameterArrayItem[] = [];
        
        if (backendTemplate.parameters && typeof backendTemplate.parameters === 'object' && !Array.isArray(backendTemplate.parameters)) {
          Object.entries(backendTemplate.parameters as Record<string, TemplateParameter>).forEach(([key, param]) => {
            let defaultValue: string | number | boolean | undefined = undefined;
            if (param.default !== undefined) {
              if (Array.isArray(param.default)) {
                defaultValue = param.default.length > 0 ? param.default[0] : undefined;
              } else {
                defaultValue = param.default;
              }
            }

            parametersArray.push({
              name: key,
              label: param.label || key,
              type: param.type || 'text',
              description: undefined,
              options: param.options,
              required: param.required || false,
              placeholder: param.placeholder,
              default: defaultValue,
              commonly_used: false
            });
          });
        }
        
        const yamlLikeTemplate: RawYAMLTemplate = {
          ...backendTemplate,
          parameters: parametersArray
        };
        
        if (isValidBackendTemplate(yamlLikeTemplate)) {
          const adapted = adaptBackendTemplate(yamlLikeTemplate);
          results.push(adapted);
        }
      } else {
        if (isValidBackendTemplate(template)) {
          const adapted = adaptBackendTemplate(template);
          results.push(adapted);
        }
      }
    } catch {
      continue;
    }
  }
  
  return results;
}

export function adaptStyleProfileCollection(extendedProfiles: unknown[]): StyleProfile[] {
  if (!Array.isArray(extendedProfiles)) return [];

  const results: StyleProfile[] = [];
  
  for (let i = 0; i < extendedProfiles.length; i++) {
    const profile = extendedProfiles[i];
    
    try {
      if (isValidExtendedStyleProfile(profile)) {
        const adapted = adaptExtendedStyleProfile(profile);
        results.push(adapted);
      }
    } catch {
      continue;
    }
  }
  
  return results;
}

export function isValidBackendTemplate(obj: unknown): obj is BackendTemplate | RawYAMLTemplate {
  if (!obj || typeof obj !== 'object') return false;
  
  const template = obj as Record<string, unknown>;
  
  const hasId = typeof template.id === 'string' && template.id.length > 0;
  const hasName = typeof template.name === 'string' && template.name.length > 0;
  
  const hasValidParameters = !template.parameters || 
    Array.isArray(template.parameters) ||
    (typeof template.parameters === 'object' && template.parameters !== null && !Array.isArray(template.parameters));
    
  return hasId && hasName && hasValidParameters;
}

export function isValidExtendedStyleProfile(obj: unknown): obj is ExtendedStyleProfile {
  if (!obj || typeof obj !== 'object') return false;
  
  const profile = obj as Record<string, unknown>;
  
  const hasId = typeof profile.id === 'string' && profile.id.length > 0;
  const hasName = typeof profile.name === 'string' && profile.name.length > 0;
  
  return hasId && hasName;
}

export function safeAdaptBackendTemplate(obj: unknown): ContentTemplate | null {
  try {
    if (isValidBackendTemplate(obj)) {
      return adaptBackendTemplate(obj);
    }
    return null;
  } catch {
    return null;
  }
}

export function safeAdaptExtendedStyleProfile(obj: unknown): StyleProfile | null {
  try {
    if (isValidExtendedStyleProfile(obj)) {
      return adaptExtendedStyleProfile(obj);
    }
    return null;
  } catch {
    return null;
  }
}

export function debugTemplateData(templates: unknown): Record<string, unknown> {
  return {
    type: typeof templates,
    isArray: Array.isArray(templates),
    length: Array.isArray(templates) ? templates.length : 'N/A',
    sample: Array.isArray(templates) ? templates[0] : templates,
    allIds: Array.isArray(templates)
      ? templates.map((t: unknown) =>
          typeof t === 'object' && t !== null && 'id' in t && typeof (t as { id?: unknown }).id === 'string'
            ? (t as { id: string }).id
            : 'no-id'
        )
      : 'N/A'
  };
}