import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    styles: [
      'educational_expert',
      'founder_storytelling',
      'ai_news_brief',
      'technical_dive',
      'phd_lit_review',
    ],
  });
}
