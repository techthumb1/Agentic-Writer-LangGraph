import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { TemplateMetadata, APIResponse } from '@/types';
import { readYamlFromDir } from '@/lib/file-loader';

const JSON_HEADERS = {
  'Content-Type': 'application/json',
  'Access-Control-Allow-Origin': '*',
};

export async function GET() {
  try {
    // Load from YAML files (fallback or hybrid setup)
    const templates = await readYamlFromDir<TemplateMetadata>('content-templates');

    const response: APIResponse<{ items: TemplateMetadata[] }> = {
      success: true,
      data: { items: templates },
    };

    return new NextResponse(JSON.stringify(response), {
      status: 200,
      headers: JSON_HEADERS,
    });
  } catch (error) {
    const errRes: APIResponse<null> = {
      success: false,
      error: {
        code: 'TEMPLATE_LOAD_FAILED',
        message: 'Could not load templates from file system',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
    };

    return new NextResponse(JSON.stringify(errRes), {
      status: 500,
      headers: JSON_HEADERS,
    });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

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

