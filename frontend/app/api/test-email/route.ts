// File: frontend/app/api/test-email/route.ts
// Debug endpoint to test SMTP configuration
// WHY: Verify email sending without full registration flow
// RELEVANT FILES: lib/email.ts, .env.local

import { NextResponse } from 'next/server';
import { sendConfirmationEmail } from '@/lib/email';

export async function GET() {
  try {
    console.log('📧 Testing email send...');
    await sendConfirmationEmail('robinsonjason90@yahoo.com', 'Test User');
    
    return NextResponse.json({ 
      success: true, 
      message: 'Email sent - check inbox' 
    });
  } catch (error) {
    console.error('❌ Email error:', error);
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}