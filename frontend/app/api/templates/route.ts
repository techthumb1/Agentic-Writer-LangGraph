// app/api/templates/route.ts
// Updated to handle dynamic template structures with complex parameters and sections
import { NextRequest, NextResponse } from 'next/server';
// File: frontend/app/api/templates/route.ts

import { promises as fs } from 'fs';
import * as yaml from 'yaml';
import path from 'path';

export async function GET() {
  try {
    console.log('🔍 Template API: Starting template loading...');
    
    // Define multiple possible template directory paths
    const possiblePaths = [
      path.join(process.cwd(), 'data', 'content_templates'),
      path.join(process.cwd(), '..', 'data', 'content_templates'),
      path.join(process.cwd(), 'frontend', '..', 'data', 'content_templates'),
    ];

    let templatesDir = '';
    let dirExists = false;

    // Find the correct templates directory
    for (const templatePath of possiblePaths) {
      try {
        await fs.access(templatePath);
        templatesDir = templatePath;
        dirExists = true;
        console.log(`✅ Found templates directory at: ${templatePath}`);
        break;
      } catch (error) {
        console.log(`❌ Directory not found: ${templatePath}`);
      }
    }

    if (!dirExists) {
      console.error('❌ No content_templates directory found in any expected location');
      return NextResponse.json({ error: 'Templates directory not found' }, { status: 404 });
    }
const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;

console.log('🔑 [TEMPLATES] Environment check:', {
  hasBaseUrl: !!FASTAPI_BASE_URL,
  hasApiKey: !!FASTAPI_API_KEY,
  baseUrl: FASTAPI_BASE_URL,
  keyPreview: FASTAPI_API_KEY ? `${FASTAPI_API_KEY.substring(0, 10)}...` : 'MISSING'
});

// Enhanced interface to handle both old and new template structures
interface BackendTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  
  // Core fields (both old and new formats)
  difficulty?: string;
  complexity?: string; // Old format fallback
  estimatedLength?: string;
  target_length?: {
    min_words?: number;
    max_words?: number;
    optimal_words?: number;
  } | string | number; // Old format fallback
  targetAudience?: string;
  icon?: string;
  tags?: string[];
  
  // Section handling (new dynamic format)
  sections?: Array<{
    title?: string;
    required?: boolean;
    name?: string;
    description?: string;
  }> | string[];
  suggested_sections?: Array<{
    name: string;
    description: string;
    required: boolean;
    content_type: string;
    specifications: string[];
  }>;
  
  // Parameter handling (new dynamic format)
  parameters?: Array<{
    name: string;
    type: string;
    label: string;
    description: string;
    required?: boolean;
    commonly_used?: boolean;
    affects_approach?: boolean;
    affects_scope?: boolean;
    affects_tone?: boolean;
    options?: Record<string, string>;
  }> | Record<string, unknown>; // Support old simple format too
  
  // Enhanced fields
  metadata?: Record<string, unknown>;
  filename?: string;
  instructions?: string;
  template_type?: string;
  content_format?: string;
  output_structure?: string;
  generation_mode?: string;
  
  // Template-specific configurations
  section_order?: string[];
  tone?: Record<string, unknown>;
  validation_rules?: string[];
  proposal_specs?: Record<string, unknown>;
  
  // Quality and requirements
  requirements?: Record<string, unknown>;
  quality_targets?: Record<string, unknown>;
  
  // Backwards compatibility
  [key: string]: unknown;
}

// Transform complex parameters to frontend-friendly format
function transformParameters(params: unknown): Record<string, unknown> {
  if (!params) return {};
  
  // If it's already a simple object, return as-is
  if (!Array.isArray(params)) {
    return params as Record<string, unknown>;
  }
  
  // Transform array of parameter objects to object with defaults
  const transformed: Record<string, unknown> = {};
  
  (params as Array<Record<string, unknown>>).forEach((param) => {
    if (param.name && typeof param.name === 'string') {
      transformed[param.name] = {
        type: param.type || 'text',
        label: param.label || param.name,
        description: param.description || '',
        required: param.required || false,
        commonly_used: param.commonly_used || false,
        affects_approach: param.affects_approach || false,
        affects_scope: param.affects_scope || false,
        affects_tone: param.affects_tone || false,
        options: param.options || null,
        default: param.default || ''
      };
    }
  });
  
  return transformed;
}

// Transform sections to unified format
function transformSections(template: BackendTemplate): Array<{
  name: string;
  description: string;
  required: boolean;
  content_type: string;
  specifications: string[];
  title: string;
}> {
  // Priority: suggested_sections > sections > empty array
  if (template.suggested_sections && Array.isArray(template.suggested_sections)) {
    return template.suggested_sections.map((section) => ({
      name: (section as Record<string, unknown>).name as string || (section as Record<string, unknown>).title as string || '',
      description: (section as Record<string, unknown>).description as string || '',
      required: (section as Record<string, unknown>).required as boolean || false,
      content_type: (section as Record<string, unknown>).content_type as string || 'standard',
      specifications: (section as Record<string, unknown>).specifications as string[] || [],
      title: (section as Record<string, unknown>).title as string || (section as Record<string, unknown>).name as string || ''
    }));
  }
  
  if (template.sections && Array.isArray(template.sections)) {
    return template.sections.map((section) => {
      if (typeof section === 'string') {
        return {
          name: section,
          description: `Content for ${section}`,
          required: true,
          content_type: 'standard',
          specifications: [],
          title: section
        };
      }
      const sectionObj = section as Record<string, unknown>;
      return {
        name: sectionObj.name as string || sectionObj.title as string || 'untitled',
        description: sectionObj.description as string || '',
        required: sectionObj.required as boolean || false,
        content_type: sectionObj.content_type as string || 'standard',
        specifications: sectionObj.specifications as string[] || [],
        title: sectionObj.title as string || sectionObj.name as string || 'untitled'
      };
    });
  }
  
  return [];
}

// Extract target length in a unified way
function extractTargetLength(template: BackendTemplate): string | null {
  if (template.estimatedLength) {
    return template.estimatedLength;
  }
  
  if (template.target_length) {
    if (typeof template.target_length === 'object') {
      const tl = template.target_length as { optimal_words?: number; min_words?: number; max_words?: number };
      if (tl.optimal_words) {
        return `${tl.optimal_words} words`;
      }
      if (tl.min_words && tl.max_words) {
        return `${tl.min_words}-${tl.max_words} words`;
      }
    }
    return String(template.target_length);
  }
  
  return null;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = searchParams.get('page') || '1';
    const limit = searchParams.get('limit') || '100';
    const search = searchParams.get('search') || '';
    const category = searchParams.get('category') || '';

    console.log(`🔍 [TEMPLATES] Fetching templates - page: ${page}, limit: ${limit}, search: "${search}", category: "${category}"`);

    // Build query parameters for backend
    const params = new URLSearchParams({
      page,
      limit,
      ...(search && { search }),
      ...(category && { category }),
    });

    console.log('🔍 [TEMPLATES] Making request to:', `${FASTAPI_BASE_URL}/api/templates?${params}`);

    const response = await fetch(`${FASTAPI_BASE_URL}/api/templates?${params}`, {
      method: 'GET',
      headers: {
        ...(FASTAPI_API_KEY && { 'Authorization': `Bearer ${FASTAPI_API_KEY}` }),
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      signal: AbortSignal.timeout(10000), // 10 second timeout
    });

    if (!response.ok) {
      console.error(`❌ [TEMPLATES] Backend error: ${response.status} ${response.statusText}`);
      const errorText = await response.text();
      console.error(`❌ [TEMPLATES] Error details:`, errorText);
      throw new Error(`Backend responded with ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    console.log('🔍 [TEMPLATES] Raw backend response type:', typeof data);
    console.log('🔍 [TEMPLATES] Is array:', Array.isArray(data));
    console.log('🔍 [TEMPLATES] Response keys:', data && typeof data === 'object' ? Object.keys(data) : 'primitive type');
    console.log('🔍 [TEMPLATES] First few items:', Array.isArray(data) ? data.slice(0, 2) : 'Not an array');

    // Extract templates from various possible response structures
    let templates: BackendTemplate[] = [];
    
    if (Array.isArray(data)) {
      templates = data;
      console.log('✅ [TEMPLATES] Using direct array response');
    } else if (data.data?.items) {
      templates = data.data.items;
      console.log('✅ [TEMPLATES] Using data.data.items');
    } else if (data.items) {
      templates = data.items;
      console.log('✅ [TEMPLATES] Using data.items');
    } else if (data.templates) {
      templates = data.templates;
      console.log('✅ [TEMPLATES] Using data.templates');
    } else {
      console.warn(`⚠️ [TEMPLATES] Unexpected response structure:`, Object.keys(data || {}));
      templates = [];
    }

    console.log(`📊 [TEMPLATES] Extracted ${templates.length} templates`);

    // Transform backend templates to enhanced frontend format
    const transformedTemplates = templates.map((template) => {
      console.log('🔄 [TEMPLATES] Transforming template:', template.id, template.name);
      console.log('🔍 [TEMPLATES] Template structure keys:', Object.keys(template));
      
      // Enhanced transformation with dynamic structure support
      const transformedTemplate = {
        id: template.id,
        title: template.name || 'Untitled Template',
        description: template.description || `Template for ${template.category || 'general'}`,
        category: template.category || 'general',
        
        // Handle difficulty with fallback to complexity
        difficulty: template.difficulty || template.complexity || null,
        
        // Handle estimated length with smart extraction
        estimatedLength: extractTargetLength(template),
        
        targetAudience: template.targetAudience || null,
        icon: template.icon || null,
        tags: template.tags || [],
        
        // Enhanced parameter handling
        parameters: transformParameters(template.parameters),
        
        // Enhanced template data with all dynamic fields
        templateData: {
          // Core template info
          id: template.id,
          template_type: template.template_type || 'standard',
          content_format: template.content_format || 'standard',
          output_structure: template.output_structure || 'standard',
          generation_mode: template.generation_mode || 'standard',
          
          // Sections with dynamic structure
          sections: transformSections(template),
          section_order: template.section_order || [],
          
          // Parameters in both formats
          parameters: transformParameters(template.parameters),
          original_parameters: template.parameters, // Keep original for reference
          
          // Instructions and requirements
          instructions: template.instructions || '',
          validation_rules: template.validation_rules || [],
          
          // Tone and style
          tone: template.tone || {},
          
          // Template-specific configurations
          proposal_specs: template.proposal_specs || {},
          requirements: template.requirements || {},
          quality_targets: template.quality_targets || {},
          
          // Metadata
          metadata: template.metadata || {},
          filename: template.filename,
          
          // Keep full original data for advanced use cases
          originalData: template,
        },
        
        // Backwards compatibility fields
        instructions: template.instructions || '',
        metadata: template.metadata || {},
        
        // System fields
        isBuiltIn: true,
        isPublic: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      console.log('✅ [TEMPLATES] Transformed template structure:', {
        id: transformedTemplate.id,
        hasParameters: Object.keys(transformedTemplate.parameters).length > 0,
        hasSections: transformedTemplate.templateData.sections.length > 0,
        hasInstructions: !!transformedTemplate.instructions,
        templateType: transformedTemplate.templateData.template_type
      });
      
      return transformedTemplate;
    });

    console.log(`✅ [TEMPLATES] Successfully transformed ${transformedTemplates.length} templates`);
    console.log('🔍 [TEMPLATES] First transformed template details:', {
      id: transformedTemplates[0]?.id,
      title: transformedTemplates[0]?.title,
      parametersCount: Object.keys(transformedTemplates[0]?.parameters || {}).length,
      sectionsCount: transformedTemplates[0]?.templateData?.sections?.length || 0,
      templateType: transformedTemplates[0]?.templateData?.template_type
    });

    // Extract pagination info
    const total = Array.isArray(data) ? data.length : 
                 data.data?.total || data.total || templates.length;
    const currentPage = parseInt(page);
    const pageLimit = parseInt(limit);
    const totalPages = Math.ceil(total / pageLimit);

    const response_data = {
      templates: transformedTemplates,
      total,
      pagination: {
        page: currentPage,
        limit: pageLimit,
        total,
        totalPages,
      },
      success: true,
    };

    console.log(`🎯 [TEMPLATES] Final response:`, {
      templatesCount: response_data.templates.length,
      total: response_data.total,
      success: response_data.success,
      templateTypes: response_data.templates.map(t => ({ 
        id: t.id, 
        type: t.templateData.template_type 
      }))
    });

    return NextResponse.json(response_data);

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    console.error('❌ [TEMPLATES] API Error:', errorMessage);
    console.error('❌ [TEMPLATES] Error stack:', error instanceof Error ? error.stack : 'No stack');

    // Return error response with fallback empty data
    return NextResponse.json(
      {
        error: 'Failed to fetch templates',
        message: errorMessage,
        templates: [],
        total: 0,
        pagination: {
          page: 1,
          limit: parseInt(request.nextUrl.searchParams.get('limit') || '100'),
          total: 0,
          totalPages: 0,
        },
        success: false,
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log(`📝 [TEMPLATES] Creating new template:`, body.title);

    const response = await fetch(`${FASTAPI_BASE_URL}/api/templates`, {
      method: 'POST',
      headers: {
        ...(FASTAPI_API_KEY && { 'Authorization': `Bearer ${FASTAPI_API_KEY}` }),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ [TEMPLATES] Create error:`, errorText);
      throw new Error(`Backend responded with ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`✅ [TEMPLATES] Template created successfully:`, data.id);

    return NextResponse.json({
      success: true,
      template: data,
    });

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    console.error('❌ [TEMPLATES] Create Error:', errorMessage);

    return NextResponse.json(
      {
        error: 'Failed to create template',
        message: errorMessage,
        success: false,
      },
      { status: 500 }
    );
  }
}