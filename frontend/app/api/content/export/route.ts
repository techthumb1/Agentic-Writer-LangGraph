// app/api/content/export/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const exportSchema = z.object({
  title: z.string().min(1),
  content: z.string().min(1),
  format: z.enum(['markdown', 'html', 'pdf']),
  templateId: z.string().optional(),
  styleProfile: z.string().optional(),
});

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validatedData = exportSchema.parse(body);

    // Forward to backend for export processing
    const response = await fetch(`${BACKEND_URL}/api/content/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`
      },
      body: JSON.stringify(validatedData)
    });

    if (!response.ok) {
      throw new Error('Backend export failed');
    }

    const blob = await response.blob();
    const contentType = response.headers.get('content-type') || 'application/octet-stream';
    const filename = response.headers.get('content-disposition')?.split('filename=')[1]?.replace(/"/g, '') || 'export';

    return new NextResponse(blob, {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Cache-Control': 'no-cache',
      }
    });

  } catch (error) {
    console.error('Export error:', error);
    
    if (error instanceof z.ZodError) {
      return NextResponse.json({
        success: false,
        error: 'Invalid export request',
        details: error.errors
      }, { status: 400 });
    }
    
    return NextResponse.json({
      success: false,
      error: 'Export failed'
    }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    success: true,
    formats: [
      { id: 'markdown', name: 'Markdown', extension: 'md' },
      { id: 'html', name: 'HTML', extension: 'html' },
      { id: 'pdf', name: 'PDF', extension: 'pdf' }
    ]
  });
}