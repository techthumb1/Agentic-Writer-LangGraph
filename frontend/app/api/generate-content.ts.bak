// app/api/generate-content.ts

import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const backendUrl = process.env.BACKEND_API_URL;
    if (!backendUrl) {
      console.error('[CONFIG_ERROR] BACKEND_API_URL is not defined in environment variables.');
      return NextResponse.json({ error: 'Server configuration error' }, { status: 500 });
    }

    const response = await fetch(`${backendUrl}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      console.error('[GENERATION_FAILURE]', await response.text());
      throw new Error('Backend generation failed');
    }

    const result = await response.json();

    return NextResponse.json({
      content: result.content ?? 'No content returned.',
    });
  } catch (error) {
    console.error('[GENERATION_ERROR]', error);
    return NextResponse.json({ error: 'Generation failed' }, { status: 500 });
  }
}
