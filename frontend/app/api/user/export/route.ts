// File: frontend/app/api/user/export/route.ts
import { NextResponse } from 'next/server';
import { auth } from '@/auth';

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;

export const runtime = 'nodejs';

export async function POST() {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const response = await fetch(`${BACKEND_URL}/api/user/export`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`,
        'X-User-Id': session.user.id!
      }
    });

    if (!response.ok) {
      throw new Error('Export failed');
    }

    const jsonData = await response.text();
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `writerzroom-data-export-${timestamp}.json`;

    return new NextResponse(jsonData, {
      headers: {
        'Content-Type': 'application/json',
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Content-Length': jsonData.length.toString(),
      },
    });
  } catch (error) {
    console.error('Data export error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to export data',
        message: error instanceof Error ? error.message : 'Unknown error'
      }, 
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const response = await fetch(`${BACKEND_URL}/api/user/export/info`, {
      headers: {
        'Authorization': `Bearer ${process.env.FASTAPI_API_KEY}`,
        'X-User-Id': session.user.id!
      }
    });

    if (!response.ok) {
      throw new Error('Failed to get export info');
    }

    return NextResponse.json(await response.json());
  } catch (error) {
    console.error('Export info error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to get export information',
        message: error instanceof Error ? error.message : 'Unknown error'
      }, 
      { status: 500 }
    );
  }
}