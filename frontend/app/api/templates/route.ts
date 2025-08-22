import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;

console.log('🔑 [TEMPLATES] Environment check:', {
  hasBaseUrl: !!FASTAPI_BASE_URL,
  hasApiKey: !!FASTAPI_API_KEY,
  baseUrl: FASTAPI_BASE_URL,
  keyPreview: FASTAPI_API_KEY ? `${FASTAPI_API_KEY.substring(0, 10)}...` : 'MISSING'
});

interface BackendTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  
  difficulty?: string;
  complexity?: string;
  estimatedLength?: string;
  target_length?: {
    min_words?: number;
    max_words?: number;
    optimal_words?: number;
  } | string | number;
  targetAudience?: string;
  icon?: string;
  tags?: string[];
  
  // V2 Template fields - CRITICAL
  inputs?: Record<string, {
    required?: boolean;
    default?: unknown;
    description?: string;
    enum?: unknown[];
  }>;
  
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
  }> | Record<string, unknown>;
  
  metadata?: Record<string, unknown>;
  filename?: string;
  instructions?: string;
  template_type?: string;
  content_format?: string;
  output_structure?: string;
  generation_mode?: string;
  section_order?: string[];
  tone?: Record<string, unknown>;
  validation_rules?: string[];
  proposal_specs?: Record<string, unknown>;
  requirements?: Record<string, unknown>;
  quality_targets?: Record<string, unknown>;
  
  [key: string]: unknown;
}

function normalizeV2Template(template: BackendTemplate): BackendTemplate {
  console.log('🔄 Normalizing template:', template.id, 'has inputs:', !!template.inputs);
  
  if (!template.inputs) {
    console.log('⚠️ No inputs found, returning original');
    return template;
  }
  
  const parameters = [];
  console.log('📋 Processing inputs:', Object.keys(template.inputs));
  
  for (const [key, spec] of Object.entries(template.inputs)) {
    const param = {
      name: key,
      label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      type: Array.isArray(spec?.enum) ? 'select' : 
            typeof spec?.default === 'boolean' ? 'checkbox' :
            typeof spec?.default === 'number' ? 'number' : 'text',
      description: spec?.description || '',
      required: spec?.required || false,
      default: spec?.default || '',
      options: Array.isArray(spec?.enum)
        ? Object.fromEntries(
            (spec.enum as unknown[]).map((v) => [
              String(v),
              typeof v === 'string' ? v : JSON.stringify(v),
            ])
          )
        : undefined
    };
    
    parameters.push(param);
    console.log('✅ Created parameter:', param.name, param.type);
  }
  
  template.parameters = parameters;
  console.log('✅ Normalized template with', parameters.length, 'parameters');
  return template;
}

function transformParametersToRecord(params: unknown): Record<string, unknown> {
  if (!params) return {};
  
  if (!Array.isArray(params)) {
    return params as Record<string, unknown>;
  }
  
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

function transformSections(template: BackendTemplate): Array<{
  name: string;
  description: string;
  required: boolean;
  content_type: string;
  specifications: string[];
  title: string;
}> {
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
      signal: AbortSignal.timeout(10000),
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
    
    // Debug first template
    if (templates.length > 0) {
      console.log('🔍 First template debug:', {
        id: templates[0]?.id,
        name: templates[0]?.name,
        hasInputs: !!(templates[0]?.inputs),
        inputsKeys: templates[0]?.inputs ? Object.keys(templates[0].inputs) : [],
        hasParameters: !!(templates[0]?.parameters),
        allKeys: Object.keys(templates[0] || {})
      });
    }

    const transformedTemplates = templates.map((template) => {
      console.log('🔄 [TEMPLATES] Transforming template:', template.id, template.name);
      
      // Normalize V2 template structure
      const normalizedTemplate = normalizeV2Template(template);
      
      const transformedTemplate = {
        id: normalizedTemplate.id,
        title: normalizedTemplate.name || 'Untitled Template',
        description: normalizedTemplate.description || `Template for ${normalizedTemplate.category || 'general'}`,
        category: normalizedTemplate.category || 'general',
        difficulty: normalizedTemplate.difficulty || normalizedTemplate.complexity || null,
        estimatedLength: extractTargetLength(normalizedTemplate),
        targetAudience: normalizedTemplate.targetAudience || null,
        icon: normalizedTemplate.icon || null,
        tags: normalizedTemplate.tags || [],
        
        parameters: transformParametersToRecord(normalizedTemplate.parameters),
        
        templateData: {
          id: normalizedTemplate.id,
          template_type: normalizedTemplate.template_type || 'standard',
          content_format: normalizedTemplate.content_format || 'standard',
          output_structure: normalizedTemplate.output_structure || 'standard',
          generation_mode: normalizedTemplate.generation_mode || 'standard',
          sections: transformSections(normalizedTemplate),
          section_order: normalizedTemplate.section_order || [],
          parameters: transformParametersToRecord(normalizedTemplate.parameters),
          original_parameters: normalizedTemplate.parameters,
          instructions: normalizedTemplate.instructions || '',
          validation_rules: normalizedTemplate.validation_rules || [],
          tone: normalizedTemplate.tone || {},
          proposal_specs: normalizedTemplate.proposal_specs || {},
          requirements: normalizedTemplate.requirements || {},
          quality_targets: normalizedTemplate.quality_targets || {},
          metadata: normalizedTemplate.metadata || {},
          filename: normalizedTemplate.filename,
          originalData: normalizedTemplate,
        },
        
        instructions: normalizedTemplate.instructions || '',
        metadata: normalizedTemplate.metadata || {},
        isBuiltIn: true,
        isPublic: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      console.log('✅ [TEMPLATES] Transformed template structure:', {
        id: transformedTemplate.id,
        hasParameters: Object.keys(transformedTemplate.parameters).length > 0,
        parameterKeys: Object.keys(transformedTemplate.parameters),
        hasSections: transformedTemplate.templateData.sections.length > 0,
        hasInstructions: !!transformedTemplate.instructions,
        templateType: transformedTemplate.templateData.template_type
      });
      
      return transformedTemplate;
    });

    console.log(`✅ [TEMPLATES] Successfully transformed ${transformedTemplates.length} templates`);
    if (transformedTemplates.length > 0) {
      console.log('🔍 [TEMPLATES] First transformed template details:', {
        id: transformedTemplates[0]?.id,
        title: transformedTemplates[0]?.title,
        parametersCount: Object.keys(transformedTemplates[0]?.parameters || {}).length,
        parameterKeys: Object.keys(transformedTemplates[0]?.parameters || {}),
        sectionsCount: transformedTemplates[0]?.templateData?.sections?.length || 0,
        templateType: transformedTemplates[0]?.templateData?.template_type
      });
    }

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
      firstTemplateParameterCount: Object.keys(response_data.templates[0]?.parameters || {}).length
    });

    return NextResponse.json(response_data);

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    console.error('❌ [TEMPLATES] API Error:', errorMessage);
    console.error('❌ [TEMPLATES] Error stack:', error instanceof Error ? error.stack : 'No stack');

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