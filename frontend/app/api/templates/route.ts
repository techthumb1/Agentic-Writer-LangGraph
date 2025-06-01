import { NextResponse } from 'next/server';
import { TemplateMetadata, APIResponse } from '@/types';
import { readYamlFromDir } from '@/lib/file-loader';

export async function GET() {
  try {
    const templates = await readYamlFromDir<TemplateMetadata>('content-templates');

    const response: APIResponse<{ items: TemplateMetadata[] }> = {
      success: true,
      data: {
        items: templates,
      },
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Error loading templates:', error);

    return NextResponse.json({
      success: false,
      error: {
        code: 'TEMPLATE_LOAD_FAILED',
        message: 'Could not load templates from file system',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
    }, { status: 500 });
  }
}
