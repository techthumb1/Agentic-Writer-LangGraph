// utils/typeAdapters.ts - Enterprise Type Transformation Layer
// Enhanced with safety checks and null handling

import type { ContentTemplate, StyleProfile, TemplateParameter } from '@/types/content';

interface BackendTemplate {
  id: string;
  slug: string;
  name: string;
  description?: string;
  category?: string;
  sections?: unknown[];
  defaults?: Record<string, unknown>;
  system_prompt?: string;
  structure?: Record<string, unknown>;
  research?: Record<string, unknown>;
  parameters?: Record<string, TemplateParameter>; // ← Changed from array to object
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

// Add interface for templates with suggested parameters
interface SuggestedParameter {
  name: string;
  type: "text" | "textarea" | "number" | "select" | "checkbox" | "multiselect" | "range" | "date";
  label: string;
  description: string;
  commonly_used: boolean;
  options: string[] | undefined;
  default?: string | number | boolean;
  required?: boolean;
}

interface TemplateWithSuggestedParams {
  suggested_parameters?: SuggestedParameter[];
}

// Extend ContentTemplate to include suggested_parameters
interface ExtendedContentTemplate extends ContentTemplate {
  suggested_parameters?: SuggestedParameter[];
}

/**
 * Safely access nested properties with default values
 */
function safeGet<T>(obj: unknown, path: string, defaultValue: T): T {
  if (!obj || typeof obj !== 'object') return defaultValue;
  
  const keys = path.split('.');
  let current: unknown = obj;
  
  for (const key of keys) {
    if (current && typeof current === 'object' && current !== null && key in current) {
      // Use type assertion to access property
      current = (current as Record<string, unknown>)[key];
    } else {
      return defaultValue;
    }
  }
  
  return current !== undefined ? (current as T) : defaultValue;
}

// Helper function to validate and convert parameter type
function validateParameterType(type: string): "text" | "textarea" | "number" | "select" | "checkbox" | "multiselect" | "range" | "date" {
  const validTypes = ["text", "textarea", "number", "select", "checkbox", "multiselect", "range", "date"] as const;
  return validTypes.includes(type as typeof validTypes[number]) ? type as typeof validTypes[number] : "text";
}

// Helper function to convert suggested parameter to template parameter
function convertToTemplateParameter(suggestedParam: SuggestedParameter): TemplateParameter {
  return {
    name: suggestedParam.name,
    type: suggestedParam.type,
    label: suggestedParam.label,
    options: suggestedParam.options,
    default: suggestedParam.default,
    required: suggestedParam.required,
  };
}

/**
 * Transform backend template to frontend ContentTemplate format with safety
 */
export function adaptBackendTemplate(backendTemplate: BackendTemplate): ContentTemplate {
  // Ensure we have required fields
  if (!backendTemplate || typeof backendTemplate !== 'object') {
    throw new Error('Invalid backend template: not an object');
  }
  
  const id = safeGet(backendTemplate, 'id', '');
  const name = safeGet(backendTemplate, 'name', '');
  
  if (!id || !name) {
    throw new Error(`Invalid backend template: missing required fields - id: ${id}, name: ${name}`);
  }

  // Convert parameters object to array format expected by frontend
  const parametersArray: TemplateParameter[] = [];
  if (backendTemplate.parameters && typeof backendTemplate.parameters === 'object') {
    Object.entries(backendTemplate.parameters).forEach(([key, param]) => {
      if (param && typeof param === 'object') {
        parametersArray.push({
          ...param,
          name: key, // Override any existing name with the key
        });
      }
    });
  }

  return {
    id,
    title: name,
    description: safeGet(backendTemplate, 'description', undefined),
    category: safeGet(backendTemplate, 'category', 'general'),
    difficulty: safeGet(backendTemplate, 'category', undefined),
    estimatedLength: undefined,
    targetAudience: undefined,
    icon: undefined,
    tags: safeGet(backendTemplate, 'sections', []),
    parameters: parametersArray, // Use converted array
    templateData: {
      parameters: parametersArray,
      metadata: safeGet(backendTemplate, 'metadata', {}),
      filename: safeGet(backendTemplate, 'filename', undefined),
      sections: safeGet(backendTemplate, 'sections', undefined),
    },
    instructions: '',
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

/**
 * Transform extended style profile to frontend StyleProfile format with safety
 */
export function adaptExtendedStyleProfile(extendedProfile: ExtendedStyleProfile): StyleProfile {
  // Ensure we have required fields
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

/**
 * Batch transform arrays of backend data with safety and filtering
 */
export function adaptTemplateCollection(backendTemplates: unknown[]): ContentTemplate[] {
  if (!Array.isArray(backendTemplates)) {
    console.warn('adaptTemplateCollection: Expected array, got:', typeof backendTemplates);
    return [];
  }

  const results: ContentTemplate[] = [];
  
  for (let i = 0; i < backendTemplates.length; i++) {
    const template = backendTemplates[i];
    
    try {
      // Validate before adapting
      if (isValidBackendTemplate(template)) {
        const adapted = adaptBackendTemplate(template);
        
        // Add backward compatibility for suggested_parameters
        if (template && typeof template === 'object' && 'suggested_parameters' in template) {
          const templateWithParams = template as Record<string, unknown> & TemplateWithSuggestedParams;
          const rawSuggestedParams = templateWithParams.suggested_parameters;
          
          if (Array.isArray(rawSuggestedParams)) {
            // Type-safe conversion of suggested parameters
            const suggestedParams: SuggestedParameter[] = rawSuggestedParams
              .filter(p => p && typeof p === 'object')
              .map(p => ({
                name: String(p.name || ''),
                type: validateParameterType(String(p.type || 'text')),
                label: String(p.label || ''),
                description: String(p.description || ''),
                commonly_used: Boolean(p.commonly_used),
                options: Array.isArray(p.options) ? p.options.map(String) : undefined,
                default: p.default as string | number | boolean | undefined,
                required: Boolean(p.required),
              }))
              .filter(
                (p) =>
                  typeof p.name === 'string' && p.name.length > 0 &&
                  typeof p.label === 'string' && p.label.length > 0
              );

            // Add suggested_parameters to the adapted template
            const extendedAdapted = adapted as ExtendedContentTemplate;
            extendedAdapted.suggested_parameters = suggestedParams;
            
            // Override parameters with commonly used ones for main UI
            const commonParams = suggestedParams
              .filter(p => p.commonly_used)
              .map(convertToTemplateParameter);
              
            if (commonParams.length > 0) {
              adapted.parameters = commonParams;
            }
            
            console.log(`Adapted template "${adapted.title}" with ${suggestedParams.length} suggested parameters (${commonParams.length} commonly used)`);
          }
        }
        
        results.push(adapted);
      } else {
        console.warn(`adaptTemplateCollection: Invalid template at index ${i}:`, template);
      }
    } catch (error) {
      console.error(`adaptTemplateCollection: Error adapting template at index ${i}:`, error, template);
    }
  }
  
  console.log(`adaptTemplateCollection: Successfully adapted ${results.length} out of ${backendTemplates.length} templates`);
  return results;
}

/**
 * Batch transform arrays of extended style profiles with safety and filtering
 */
export function adaptStyleProfileCollection(extendedProfiles: unknown[]): StyleProfile[] {
  if (!Array.isArray(extendedProfiles)) {
    console.warn('adaptStyleProfileCollection: Expected array, got:', typeof extendedProfiles);
    return [];
  }

  const results: StyleProfile[] = [];
  
  for (let i = 0; i < extendedProfiles.length; i++) {
    const profile = extendedProfiles[i];
    
    try {
      // Validate before adapting
      if (isValidExtendedStyleProfile(profile)) {
        const adapted = adaptExtendedStyleProfile(profile);
        results.push(adapted);
      } else {
        console.warn(`adaptStyleProfileCollection: Invalid profile at index ${i}:`, profile);
      }
    } catch (error) {
      console.error(`adaptStyleProfileCollection: Error adapting profile at index ${i}:`, error, profile);
    }
  }
  
  console.log(`adaptStyleProfileCollection: Successfully adapted ${results.length} out of ${extendedProfiles.length} profiles`);
  return results;
}

/**
 * Type guard to check if object has required template properties
 */
export function isValidBackendTemplate(obj: unknown): obj is BackendTemplate {
  if (!obj || typeof obj !== 'object') {
    return false;
  }
  
  const template = obj as Record<string, unknown>;
  
  // Check required fields
  const hasId = typeof template.id === 'string' && template.id.length > 0;
  const hasName = typeof template.name === 'string' && template.name.length > 0;
  
  // Check optional parameters field
  const hasValidParameters = !template.parameters || (typeof template.parameters === 'object' && template.parameters !== null && !Array.isArray(template.parameters));
  return hasId && hasName && hasValidParameters;
}

/**
 * Type guard to check if object has required style profile properties
 */
export function isValidExtendedStyleProfile(obj: unknown): obj is ExtendedStyleProfile {
  if (!obj || typeof obj !== 'object') {
    return false;
  }
  
  const profile = obj as Record<string, unknown>;
  
  // Check required fields
  const hasId = typeof profile.id === 'string' && profile.id.length > 0;
  const hasName = typeof profile.name === 'string' && profile.name.length > 0;
  
  return hasId && hasName;
}

/**
 * Safe adapter with validation for templates
 */
export function safeAdaptBackendTemplate(obj: unknown): ContentTemplate | null {
  try {
    if (isValidBackendTemplate(obj)) {
      return adaptBackendTemplate(obj);
    }
    return null;
  } catch (error) {
    console.error('safeAdaptBackendTemplate: Error adapting template:', error, obj);
    return null;
  }
}

/**
 * Safe adapter with validation for style profiles
 */
export function safeAdaptExtendedStyleProfile(obj: unknown): StyleProfile | null {
  try {
    if (isValidExtendedStyleProfile(obj)) {
      return adaptExtendedStyleProfile(obj);
    }
    return null;
  } catch (error) {
    console.error('safeAdaptExtendedStyleProfile: Error adapting profile:', error, obj);
    return null;
  }
}

/**
 * Debug helper to log template data structure
 */
export function debugTemplateData(templates: unknown, source: string = 'unknown') {
  console.log(`🔍 Template data from ${source}:`, {
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
  });
}