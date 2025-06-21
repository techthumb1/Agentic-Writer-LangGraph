// frontend/app/api/templates/route.ts
import { NextRequest, NextResponse } from 'next/server';
import type { APIResponse, BackendTemplate } from '@/types/api';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const JSON_HEADERS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
};

export async function GET() {
  try {
    console.log('📤 Fetching templates from FastAPI backend');

    const response = await fetch(`${BACKEND_URL}/api/templates`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      // Add cache control for better performance
      next: { revalidate: 300 } // Cache for 5 minutes
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ FastAPI backend error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      
      // Fallback to local file loading if backend is unavailable
      try {
        console.log('🔄 Falling back to local template loading');
        const { readYamlFromDir } = await import('@/lib/file-loader');
        
        interface LocalTemplate {
          name: string;
          description?: string;
          parameters?: Record<string, unknown>;
          [key: string]: unknown;
        }
        
        const templates = await readYamlFromDir<LocalTemplate>('content-templates');
        
        return new NextResponse(JSON.stringify({
          success: true,
          data: { items: templates },
          fallback: true
        }), {
          status: 200,
          headers: JSON_HEADERS,
        });
      } catch (fallbackError) {
        return new NextResponse(JSON.stringify({
          success: false,
          error: {
            code: 'TEMPLATE_LOAD_FAILED',
            message: 'Could not load templates from backend or local files',
            details: {
              backendError: errorText,
              fallbackError: fallbackError instanceof Error ? fallbackError.message : String(fallbackError),
            },
          },
        }), {
          status: 500,
          headers: JSON_HEADERS,
        });
      }
    }

    const data = await response.json();
    console.log('✅ Templates loaded from FastAPI:', {
      count: data.data?.items?.length || 0,
      success: data.success
    });

    // Transform backend response to match your frontend's expected format
    const transformedResponse: APIResponse<{ items: BackendTemplate[] }> = {
      success: data.success,
      data: {
        items: data.data?.items?.map((template: BackendTemplate) => ({
          id: template.id,
          slug: template.slug,
          name: template.name,
          description: template.description,
          category: template.category,
          parameters: template.parameters,
          metadata: template.metadata,
          version: template.version,
          filename: template.filename
        })) || []
      }
    };

    return new NextResponse(JSON.stringify(transformedResponse), {
      status: 200,
      headers: JSON_HEADERS,
    });

  } catch (error) {
    console.error('🚨 Templates API error:', error);
    
    return new NextResponse(JSON.stringify({
      success: false,
      error: {
        code: 'TEMPLATE_PROXY_FAILED',
        message: 'Failed to fetch templates',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
    }), {
      status: 500,
      headers: JSON_HEADERS,
    });
  }
}

// Keep existing POST, PUT, DELETE methods for local template management
export async function POST(request: NextRequest) {
  try {
    // First try to create in backend
    const body = await request.json();
    
    const backendResponse = await fetch(`${BACKEND_URL}/api/templates`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (backendResponse.ok) {
      const data = await backendResponse.json();
      return NextResponse.json(data);
    }

    // Fallback to local creation (your existing logic)
    const { prisma } = await import('@/lib/prisma');
    
    const created = await prisma.template.create({
      data: {
        slug: body.slug,
        name: body.name,
        description: body.description || null,
        parameters: body.parameters,
      },
    });

    return new NextResponse(JSON.stringify({ success: true, data: created }), {
      status: 201,
      headers: JSON_HEADERS,
    });
  } catch (error) {
    return new NextResponse(
      JSON.stringify({
        success: false,
        error: {
          code: 'TEMPLATE_CREATE_FAILED',
          message: 'Failed to create template',
          details: error instanceof Error ? error.message : 'Unknown error',
        },
      }),
      { status: 500, headers: JSON_HEADERS }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();

    if (!body.id) {
      return new NextResponse(
        JSON.stringify({
          success: false,
          error: {
            code: 'MISSING_ID',
            message: 'Template ID is required for update',
            details: null,
          },
        }),
        { status: 400, headers: JSON_HEADERS }
      );
    }

    const { prisma } = await import('@/lib/prisma');

    const updated = await prisma.template.update({
      where: { id: body.id },
      data: {
        slug: body.slug,
        name: body.name,
        description: body.description || null,
        parameters: body.parameters,
      },
    });

    return new NextResponse(JSON.stringify({ success: true, data: updated }), {
      status: 200,
      headers: JSON_HEADERS,
    });
  } catch (error) {
    return new NextResponse(
      JSON.stringify({
        success: false,
        error: {
          code: 'TEMPLATE_UPDATE_FAILED',
          message: 'Failed to update template',
          details: error instanceof Error ? error.message : 'Unknown error',
        },
      }),
      { status: 500, headers: JSON_HEADERS }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { id } = await request.json();

    if (!id) {
      return new NextResponse(
        JSON.stringify({
          success: false,
          error: {
            code: 'MISSING_ID',
            message: 'Template ID is required for deletion',
            details: null,
          },
        }),
        { status: 400, headers: JSON_HEADERS }
      );
    }

    const { prisma } = await import('@/lib/prisma');

    await prisma.template.delete({
      where: { id },
    });

    return new NextResponse(
      JSON.stringify({ success: true, message: 'Template deleted successfully' }),
      { status: 200, headers: JSON_HEADERS }
    );
  } catch (error) {
    return new NextResponse(
      JSON.stringify({
        success: false,
        error: {
          code: 'TEMPLATE_DELETE_FAILED',
          message: 'Failed to delete template',
          details: error instanceof Error ? error.message : 'Unknown error',
        },
      }),
      { status: 500, headers: JSON_HEADERS }
    );
  }
}