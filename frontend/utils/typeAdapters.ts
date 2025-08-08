// utils/typeAdapters.ts - Enterprise Type Transformation Layer
// Enhanced with safety checks and null handling
// Updated to handle array-based parameters from YAML templates
// Compatible with existing ContentTemplate interface
// FIXED: TypeScript errors resolved

import type { ContentTemplate, StyleProfile, TemplateParameter, TemplateSection } from '@/types/content';

// Raw template structure from YAML files (what we receive from backend)
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
  // YAML files have array-based parameters
  parameters?: ParameterArrayItem[];
  suggested_sections?: Array<{
    name: string;
    description: string;
  }>;
  instructions?: string;
  metadata?: Record<string, unknown>;
}

// Backend template interface (existing structure)
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
  // Can be either object (legacy) or array (new YAML)
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

// Parameter array type for conversion
interface ParameterArrayItem {
  name: string;
  type: string;
  label: string;
  description?: string;
  options?: string[] | Record<string, string>; // FIXED: Allow both array and object
  commonly_used?: boolean;
  required?: boolean;
  placeholder?: string;
  default?: string | number | boolean | string[];
}

// Template collection response interfaces
interface TemplateCollectionResponse {
  templates?: unknown[];
  data?: {
    items?: unknown[];
  } | unknown[];
  results?: unknown[];
}

// Type guard for template collection response
function isTemplateCollectionResponse(obj: unknown): obj is TemplateCollectionResponse {
  return typeof obj === 'object' && obj !== null;
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
  // Handle "string" and "boolean" type conversions
  if (type === "string") {
    return "text";
  }
  if (type === "boolean") {
    return "checkbox";
  }
  return validTypes.includes(type as typeof validTypes[number]) ? type as typeof validTypes[number] : "text";
}

// Helper function to normalize options to string array
function normalizeOptions(options?: string[] | Record<string, string>): string[] | undefined {
  if (!options) return undefined;
  
  if (Array.isArray(options)) {
    return options;
  }
  
  if (typeof options === 'object') {
    // Convert Record<string, string> to string array using values
    return Object.values(options);
  }
  
  return undefined;
}

// Helper function to convert array-based parameters to object-based parameters (for ContentTemplate)
function convertParametersArrayToObject(
  parametersArray?: ParameterArrayItem[]
): Record<string, TemplateParameter> {
  if (!parametersArray || !Array.isArray(parametersArray)) {
    return {};
  }

  const parametersObject: Record<string, TemplateParameter> = {};

  console.log(`🔍 Converting ${parametersArray.length} parameters from array to object format`);

  parametersArray.forEach(param => {
    if (!param.name) {
      console.warn('Parameter missing name, skipping:', param);
      return;
    }

    // Ensure default value is compatible with TemplateParameter
    let defaultValue: string | number | boolean | undefined = undefined;
    if (param.default !== undefined) {
      if (Array.isArray(param.default)) {
        // Convert array to first element or undefined
        defaultValue = param.default.length > 0 ? param.default[0] : undefined;
        console.warn(`Parameter ${param.name} has array default value, using first element:`, defaultValue);
      } else {
        defaultValue = param.default;
      }
    }

    parametersObject[param.name] = {
      name: param.name,
      label: param.label || param.name,
      type: validateParameterType(param.type),
      options: normalizeOptions(param.options), // FIXED: Normalize options
      required: param.required ?? false,
      placeholder: param.placeholder,
      default: defaultValue,
      // Remove description field since it's not in TemplateParameter interface
    };

    console.log(`✅ Converted parameter: ${param.name} (${param.type} → ${parametersObject[param.name].type})`);
  });

  return parametersObject;
}

/**
 * Transform backend template to frontend ContentTemplate format with safety
 */
export function adaptBackendTemplate(backendTemplate: BackendTemplate | RawYAMLTemplate): ContentTemplate {
  // Ensure we have required fields
  if (!backendTemplate || typeof backendTemplate !== 'object') {
    throw new Error('Invalid backend template: not an object');
  }
  
  const id = safeGet(backendTemplate, 'id', '');
  const name = safeGet(backendTemplate, 'name', '');
  
  if (!id || !name) {
    throw new Error(`Invalid backend template: missing required fields - id: ${id}, name: ${name}`);
  }

  // Convert parameters (both array and object formats) to object format expected by ContentTemplate
  let parametersObject: Record<string, TemplateParameter> = {};
  
  if (backendTemplate.parameters) {
    if (Array.isArray(backendTemplate.parameters)) {
      // New YAML format with array-based parameters
      console.log(`🔍 Converting array-based parameters for template: ${name}`);
      parametersObject = convertParametersArrayToObject(backendTemplate.parameters);
    } else if (typeof backendTemplate.parameters === 'object') {
      // Legacy object format
      console.log(`🔍 Using existing object-based parameters for template: ${name}`);
      parametersObject = backendTemplate.parameters as Record<string, TemplateParameter>;
    }
  }

  console.log(`✅ Template "${name}" has ${Object.keys(parametersObject).length} parameters:`, Object.keys(parametersObject));

  // FIXED: Convert to Record<string, TemplateParameter> instead of array
  const parametersRecord: Record<string, TemplateParameter> = parametersObject;

  // Convert to ContentTemplate format (matching your existing interface)
  const contentTemplate: ContentTemplate = {
    id,
    title: name,
    description: safeGet(backendTemplate, 'description', ''),
    category: safeGet(backendTemplate, 'category', 'general'),
    difficulty: safeGet(backendTemplate, 'difficulty', undefined),
    estimatedLength: safeGet(backendTemplate, 'estimatedLength', undefined),
    targetAudience: safeGet(backendTemplate, 'targetAudience', undefined),
    icon: safeGet(backendTemplate, 'icon', undefined),
    tags: safeGet(backendTemplate, 'tags', []),
    parameters: parametersRecord, // FIXED: Use Record instead of array
    templateData: {
      id,
      template_type: 'standard',
      content_format: 'standard',
      output_structure: 'standard',
      generation_mode: 'standard',
      sections: safeGet(backendTemplate, 'sections', []) as TemplateSection[], // FIXED: Provide default empty array
      section_order: [],
      parameters: parametersRecord, // FIXED: Use Record instead of array
      original_parameters: backendTemplate.parameters,
      instructions: safeGet(backendTemplate, 'instructions', ''), // FIXED: Provide default empty string
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

  return contentTemplate;
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
export function adaptTemplateCollection(backendTemplates: unknown): ContentTemplate[] {
  console.log('🔍 adaptTemplateCollection called with:', typeof backendTemplates, Array.isArray(backendTemplates));
  
  // Handle different possible response formats
  let templatesArray: unknown[];
  
  if (Array.isArray(backendTemplates)) {
    templatesArray = backendTemplates;
  } else if (isTemplateCollectionResponse(backendTemplates)) {
    // Check for common API response formats
    const response = backendTemplates as TemplateCollectionResponse;
    if (Array.isArray(response.templates)) {
      templatesArray = response.templates;
    } else if (response.data && Array.isArray((response.data as { items?: unknown[] }).items)) {
      templatesArray = (response.data as { items: unknown[] }).items;
    } else if (Array.isArray(response.data)) {
      templatesArray = response.data;
    } else if (Array.isArray(response.results)) {
      templatesArray = response.results;
    } else {
      console.warn('adaptTemplateCollection: Unknown template response format:', backendTemplates);
      console.warn('Available keys:', Object.keys(response));
      return [];
    }
  } else {
    console.warn('adaptTemplateCollection: Expected array or object, got:', typeof backendTemplates);
    return [];
  }

  console.log(`🔍 Processing ${templatesArray.length} raw templates`);

  const results: ContentTemplate[] = [];
  let successCount = 0;
  let errorCount = 0;
  
  for (let i = 0; i < templatesArray.length; i++) {
    const template = templatesArray[i];
    
    try {
      // Check if this is a backend template (with object parameters) or YAML template (with array parameters)
      const templateObj = template as Record<string, unknown>;
      const hasObjectParameters = templateObj && typeof templateObj === 'object' && 
        templateObj.parameters && typeof templateObj.parameters === 'object' && !Array.isArray(templateObj.parameters);
      
      if (hasObjectParameters) {
        // Backend template with object-based parameters - convert to array format
        const backendTemplate = template as BackendTemplate;
        const parametersArray: ParameterArrayItem[] = [];
        
        if (backendTemplate.parameters && typeof backendTemplate.parameters === 'object' && !Array.isArray(backendTemplate.parameters)) {
          Object.entries(backendTemplate.parameters as Record<string, TemplateParameter>).forEach(([key, param]) => {
            // Ensure default value compatibility
            let defaultValue: string | number | boolean | undefined = undefined;
            if (param.default !== undefined) {
              if (Array.isArray(param.default)) {
                defaultValue = param.default.length > 0 ? param.default[0] : undefined;
                console.warn(`Parameter ${key} has array default value, using first element:`, defaultValue);
              } else {
                defaultValue = param.default;
              }
            }

            parametersArray.push({
              name: key,
              label: param.label || key,
              type: param.type || 'text',
              description: undefined, // TemplateParameter doesn't have description
              options: param.options, // FIXED: Keep original options type
              required: param.required || false,
              placeholder: param.placeholder,
              default: defaultValue,
              commonly_used: false // Default value
            });
          });
        }
        
        // Create a YAML-like template structure
        const yamlLikeTemplate: RawYAMLTemplate = {
          ...backendTemplate,
          parameters: parametersArray
        };
        
        console.log(`🔄 Converted backend template "${backendTemplate.name}" with ${parametersArray.length} parameters`);
        
        if (isValidBackendTemplate(yamlLikeTemplate)) {
          const adapted = adaptBackendTemplate(yamlLikeTemplate);
          results.push(adapted);
          successCount++;
        }
      } else {
        // YAML template with array-based parameters (existing logic)
        if (isValidBackendTemplate(template)) {
          const adapted = adaptBackendTemplate(template);
          results.push(adapted);
          successCount++;
        }
      }
      
    } catch (error) {
      errorCount++;
      console.error(`🚨 Error adapting template at index ${i}:`, error, template);
    }
  }
  
  console.log(`✅ adaptTemplateCollection: Successfully adapted ${successCount} out of ${templatesArray.length} templates`);
  
  if (errorCount > 0) {
    console.warn(`⚠️  ${errorCount} templates failed to adapt`);
  }
  
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
export function isValidBackendTemplate(obj: unknown): obj is BackendTemplate | RawYAMLTemplate {
  if (!obj || typeof obj !== 'object') {
    return false;
  }
  
  const template = obj as Record<string, unknown>;
  
  // Check required fields
  const hasId = typeof template.id === 'string' && template.id.length > 0;
  const hasName = typeof template.name === 'string' && template.name.length > 0;
  
  // Check optional parameters field (now supports both array and object)
  const hasValidParameters = !template.parameters || 
    Array.isArray(template.parameters) ||
    (typeof template.parameters === 'object' && template.parameters !== null && !Array.isArray(template.parameters));
    
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