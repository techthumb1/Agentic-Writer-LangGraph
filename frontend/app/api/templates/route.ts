// app/api/templates/route.ts
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
  estimatedLength?: string;
  targetAudience?: string;
  icon?: string;
  tags?: string[];
  sections?: unknown[];
  parameters?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
  filename?: string;
  instructions?: string;
  [key: string]: unknown;
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

    // ✅ FIX: Backend returns templates directly as an array
    let templates: BackendTemplate[] = [];
    
    if (Array.isArray(data)) {
      // Backend returns templates directly as an array
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

    // Transform backend templates to frontend format
    const transformedTemplates = templates.map((template) => {
      console.log('🔄 [TEMPLATES] Transforming template:', template.id, template.name);
      
      return {
        id: template.id,
        title: template.name || 'Untitled Template',
        description: template.description || `Template for ${template.category || 'general'}`,
        category: template.category || 'general',
        difficulty: template.difficulty || null,
        estimatedLength: template.estimatedLength || null,
        targetAudience: template.targetAudience || null,
        icon: template.icon || null,
        tags: template.tags || [],
        parameters: template.parameters || {},
        templateData: {
          parameters: template.parameters || {},
          metadata: template.metadata || {},
          filename: template.filename,
          sections: template.sections,
          instructions: template.instructions,
          originalData: template,
        },
        instructions: template.instructions || '',
        metadata: template.metadata || {},
        isBuiltIn: true,
        isPublic: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    });

    console.log(`✅ [TEMPLATES] Successfully transformed ${transformedTemplates.length} templates`);
    console.log('🔍 [TEMPLATES] First transformed template:', transformedTemplates[0]);

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
      success: response_data.success
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