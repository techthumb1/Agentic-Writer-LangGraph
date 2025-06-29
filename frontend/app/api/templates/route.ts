// app/api/templates/route.ts
import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY || 'your-api-key-here';

interface BackendTemplate {
  id: string;
  platform?: string;
  title: string;
  audience?: string;
  tone?: string;
  length?: string;
  code?: string;
  tags?: string[];
  system_prompt?: string;
  parameters?: Record<string, unknown>;
  [key: string]: unknown;
}

interface BackendResponse {
  success?: boolean;
  data?: {
    items?: BackendTemplate[];
    templates?: BackendTemplate[];
    pagination?: {
      total?: number;
      page?: number;
      limit?: number;
      totalPages?: number;
    };
    total?: number; // Sometimes total is at root level
  };
  items?: BackendTemplate[]; // Sometimes items are at root level
  templates?: BackendTemplate[]; // Sometimes templates are at root level
  total?: number;
  pagination?: {
    total?: number;
    page?: number;
    limit?: number;
    totalPages?: number;
  };
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

    const response = await fetch(`${FASTAPI_BASE_URL}/api/templates?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(10000), // 10 second timeout
    });

    if (!response.ok) {
      console.error(`❌ [TEMPLATES] Backend error: ${response.status} ${response.statusText}`);
      throw new Error(`Backend responded with ${response.status}: ${response.statusText}`);
    }

    const data: BackendResponse = await response.json();
    console.log(`📊 [TEMPLATES] Backend response structure:`, {
      hasData: !!data.data,
      hasItems: !!(data.data?.items || data.items || data.templates),
      hasPagination: !!(data.data?.pagination || data.pagination),
      itemsCount: (data.data?.items || data.items || data.templates || []).length,
    });

    // Extract templates from various possible response structures
    let templates: BackendTemplate[] = [];
    
    if (data.data?.items) {
      templates = data.data.items;
    } else if (data.data?.templates) {
      templates = data.data.templates;
    } else if (data.items) {
      templates = data.items;
    } else if (data.templates) {
      templates = data.templates;
    } else if (Array.isArray(data)) {
      templates = data as BackendTemplate[];
    } else {
      console.warn(`⚠️ [TEMPLATES] Unexpected response structure:`, Object.keys(data));
      templates = [];
    }

    // Extract pagination info with fallbacks
    const pagination = data.data?.pagination || data.pagination || {};
    const total = pagination.total ?? data.data?.total ?? data.total ?? templates.length;
    const currentPage = parseInt(page);
    const pageLimit = parseInt(limit);
    const totalPages = Math.ceil(total / pageLimit);

    // Transform backend templates to frontend format
    const transformedTemplates = templates.map((template) => ({
      id: template.id,
      title: template.title || 'Untitled Template',
      description: template.system_prompt || `Template for ${template.audience || 'general'} audience`,
      category: template.platform || 'general',
      difficulty: template.tone || null,
      estimatedLength: template.length || null,
      targetAudience: template.audience || null,
      icon: null,
      tags: template.tags || [],
      parameters: [],
      templateData: {
        parameters: template.parameters || {},
        system_prompt: template.system_prompt,
        code: template.code,
        originalData: template,
      },
      isBuiltIn: true,
      isPublic: true,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }));

    console.log(`✅ [TEMPLATES] Successfully transformed ${transformedTemplates.length} templates`);

    return NextResponse.json({
      templates: transformedTemplates,
      total,
      pagination: {
        page: currentPage,
        limit: pageLimit,
        total,
        totalPages,
      },
      success: true,
    });

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    console.error('❌ [TEMPLATES] API Error:', errorMessage);

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
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
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