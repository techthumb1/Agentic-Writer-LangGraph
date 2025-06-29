// utils/typeAdapters.ts - Enterprise Type Transformation Layer
// Commit 1: Create type adapters for backend/frontend alignment

import type { ContentTemplate, StyleProfile, TemplateParameter } from '@/types/content';

interface BackendTemplate {
  parameters?: TemplateParameter[]; // Make parameters optional
  id: string;
  name: string;
  description?: string;
  category?: string;
  sections?: string[];
  metadata?: Record<string, unknown>;
  filename?: string;
}

interface ExtendedStyleProfile {
  id: string;
  name: string;
  description?: string;
  category?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Transform backend template to frontend ContentTemplate format
 */
export function adaptBackendTemplate(backendTemplate: BackendTemplate): ContentTemplate {
  return {
    id: backendTemplate.id,
    title: backendTemplate.name, // Map name -> title
    description: backendTemplate.description || undefined,
    category: backendTemplate.category || 'general',
    difficulty: backendTemplate.category || undefined,
    estimatedLength: undefined,
    targetAudience: undefined,
    icon: undefined,
    tags: backendTemplate.sections || [],
    parameters: backendTemplate.parameters || [], // Handle optional parameters
    templateData: {
      parameters: backendTemplate.parameters || [],
      metadata: backendTemplate.metadata || {},
      filename: backendTemplate.filename,
      sections: backendTemplate.sections,
    },
    isBuiltIn: true,
    isPublic: true,
    createdAt: new Date(),
    updatedAt: new Date(),
  };
}

/**
 * Transform extended style profile to frontend StyleProfile format
 */
export function adaptExtendedStyleProfile(extendedProfile: ExtendedStyleProfile): StyleProfile {
  return {
    id: extendedProfile.id,
    name: extendedProfile.name,
    description: extendedProfile.description || `Style profile: ${extendedProfile.name}`,
    category: extendedProfile.category || 'general',
    icon: undefined, // Fixed: null -> undefined
    tags: [],
    profileData: {
      metadata: extendedProfile.metadata || {},
    },
    isBuiltIn: true,
    isPublic: true,
    createdAt: new Date(),
    updatedAt: new Date(),
  };
}

/**
 * Batch transform arrays of backend data
 */
export function adaptTemplateCollection(backendTemplates: BackendTemplate[]): ContentTemplate[] {
  return backendTemplates.map(template => adaptBackendTemplate(template));
}

/**
 * Batch transform arrays of extended style profiles
 */
export function adaptStyleProfileCollection(extendedProfiles: ExtendedStyleProfile[]): StyleProfile[] {
  return extendedProfiles.map(profile => adaptExtendedStyleProfile(profile));
}

/**
 * Type guard to check if object has required template properties
 */
export function isValidBackendTemplate(obj: unknown): obj is BackendTemplate {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj &&
    typeof (obj as BackendTemplate).id === 'string' &&
    typeof (obj as BackendTemplate).name === 'string' &&
    (!(obj as BackendTemplate).parameters || Array.isArray((obj as BackendTemplate).parameters))
  );
}

/**
 * Type guard to check if object has required style profile properties
 */
export function isValidExtendedStyleProfile(obj: unknown): obj is ExtendedStyleProfile {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'name' in obj &&
    typeof (obj as ExtendedStyleProfile).id === 'string' &&
    typeof (obj as ExtendedStyleProfile).name === 'string'
  );
}

/**
 * Safe adapter with validation for templates
 */
export function safeAdaptBackendTemplate(obj: unknown): ContentTemplate | null {
  if (isValidBackendTemplate(obj)) {
    return adaptBackendTemplate(obj);
  }
  return null;
}

/**
 * Safe adapter with validation for style profiles
 */
export function safeAdaptExtendedStyleProfile(obj: unknown): StyleProfile | null {
  if (isValidExtendedStyleProfile(obj)) {
    return adaptExtendedStyleProfile(obj);
  }
  return null;
}