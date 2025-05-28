// app/api/generate-content.ts

import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const body = await req.json();

  try {
    const res = await fetch(`${process.env.BACKEND_API_URL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      throw new Error('Backend generation failed');
    }

    const data = await res.json();
    return NextResponse.json({ content: data.content || 'No content returned.' });
  } catch (error) {
    console.error('[GENERATION_ERROR]', error);
    return NextResponse.json({ error: 'Generation failed' }, { status: 500 });
  }
}
