import { NextResponse } from 'next/server';
import { TemplateMetadata, APIResponse } from '@/types';
import { readYamlFromDir } from '@/lib/file-loader';

export async function GET() {
  try {
    // Load all templates from the 'content-templates/' YAML directory
    const templates = await readYamlFromDir<TemplateMetadata>('content-templates');

    const response: APIResponse<{ items: TemplateMetadata[] }> = {
      success: true,
      data: {
        items: templates,
      },
    };

    return new NextResponse(JSON.stringify(response), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*', // ✅ CORS header
      },
    });
  } catch (error) {
    console.error('TEMPLATE_LOAD_FAILED:', error);

    const errorResponse: APIResponse<null> = {
      success: false,
      error: {
        code: 'TEMPLATE_LOAD_FAILED',
        message: 'Could not load templates from file system',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
    };

    return new NextResponse(JSON.stringify(errorResponse), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*', // ✅ CORS header for error too
      },
    });
  }
}
