// frontend/hooks/useTemplates.ts - FIXED VERSION
import { useQuery } from "@tanstack/react-query";
import { Template, TemplateParameter } from "@/types/template";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000';

async function fetcher(url: string): Promise<Template[]> {
  console.log('🚀 Fetching templates from:', url);
  
  const res = await fetch(url);
  if (!res.ok) {
    const errorText = await res.text();
    console.error('❌ Templates fetch failed:', res.status, res.statusText, errorText);
    throw new Error(`Failed to fetch templates: ${res.status} ${res.statusText}`);
  }
  
  const result = await res.json();
  
  console.log('🔍 Templates API response structure:', {
    type: typeof result,
    isArray: Array.isArray(result),
    keys: result && typeof result === 'object' ? Object.keys(result) : 'not object',
    hasTemplates: result?.templates !== undefined,
    hasSuccess: result?.success !== undefined,
    templatesLength: result?.templates?.length,
    resultLength: Array.isArray(result) ? result.length : 'not array'
  });
  
  // ✅ NEW: Handle our API route format { templates: [...], success: true }
  if (result && typeof result === 'object' && result.templates && Array.isArray(result.templates)) {
    console.log(`✅ Found templates in wrapper object: ${result.templates.length} templates`);
    return result.templates;
  }
  
  // Legacy: Check for paginated response structure
  if (result.success && result.data?.items && Array.isArray(result.data.items)) {
    const templates = result.data.items.map((template: Template) => ({
      id: template.id,
      slug: template.slug || template.id,
      name: template.name,
      description: template.description || '',
      category: template.category || 'general',
      sections: template.sections || [],
      defaults: template.defaults || {},
      system_prompt: template.system_prompt,
      structure: template.structure || {},
      research: template.research || {},
      parameters: template.parameters || {},
      metadata: {
        version: template.metadata?.version || template.version || '1.0.0',
        created_by: (template.metadata as Record<string, unknown>)?.created_by as string || 'system',
        last_updated: (template.metadata as Record<string, unknown>)?.last_updated as string || new Date().toISOString(),
        parameter_flexibility: (template.metadata as Record<string, unknown>)?.parameter_flexibility as string || 'flexible'
      },
      version: template.version || '1.0.0',
      filename: template.filename
    }));
    
    console.log(`✅ Loaded ${templates.length} real templates from legacy format`);
    return templates;
  }
  
  // Fallback: Direct array
  if (Array.isArray(result)) {
    console.log(`✅ Using direct array format: ${result.length} templates`);
    return result;
  }
  
  // Enhanced error logging
  console.error('❌ Templates API error - Full result:', JSON.stringify(result, null, 2));
  console.error('❌ No valid template format found');
  
  throw new Error(result.error?.message || 'Failed to load templates - unexpected response format');
}

// ✅ FIXED: Return interface that matches component expectations
export function useTemplates() {
  const query = useQuery<Template[], Error>({
    queryKey: ['templates'],
    queryFn: async () => {
      console.log('🔄 useTemplates: Starting fetch...');
      const result = await fetcher(`${BACKEND_URL}/api/templates?page=1&limit=100`);
      
      console.log('🔍 useTemplates: Final result:', {
        type: typeof result,
        isArray: Array.isArray(result),
        length: Array.isArray(result) ? result.length : 'not array',
        firstItem: Array.isArray(result) && result.length > 0 ? result[0].id : 'none'
      });
      
      return result;
    },
    staleTime: 5 * 60 * 1000,
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // ✅ FIXED: Return both interfaces to support all components
  return {
    // Standard React Query interface (for page.tsx)
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    
    // Component-expected interface (for TemplateSelector.tsx if needed)
    templates: query.data,
  };
}

export function useTemplate(id: string) {
  const { data: templates, isLoading, error } = useTemplates();
  
  const template = Array.isArray(templates) ? templates.find(t => t.id === id) : undefined;
  
  return {
    data: template,
    isLoading,
    error: template ? null : error
  };
}

// Helper function to convert backend parameters to frontend format
export function getTemplateParametersAsArray(template: Template): TemplateParameter[] {
  if (!template.parameters) return [];
  
  return Object.entries(template.parameters).map(([key, param]) => ({
    name: key,
    label: param.label || key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    type: param.type || 'text',
    placeholder: param.placeholder,
    default: param.default,
    options: param.options,
    min: param.min,
    max: param.max,
    required: param.required || false,
    description: param.description
  }));
}