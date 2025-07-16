// frontend/app/api/generate/route.ts - ADD DEBUG LOGGING
import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;

export async function POST(request: NextRequest) {
  const requestId = randomUUID();
  
  try {
    const body = await request.json();
    
    // 🔍 ADD THIS DEBUG LOGGING
    console.log('🔍 [DEBUG] Received request body:', JSON.stringify(body, null, 2));
    console.log('🔍 [DEBUG] Environment variables:', {
      FASTAPI_BASE_URL,
      HAS_FASTAPI_API_KEY: !!FASTAPI_API_KEY,
      NODE_ENV: process.env.NODE_ENV
    });
    
    // Enterprise request validation
    if (!body.template) {
      console.log('❌ [DEBUG] Missing template field');
      return NextResponse.json(
        { 
          success: false, 
          error: 'Template ID is required',
          request_id: requestId,
          received_fields: Object.keys(body)
        },
        { status: 400 }
      );
    }
    
    if (!body.style_profile) {
      console.log('❌ [DEBUG] Missing style_profile field');
      return NextResponse.json(
        { 
          success: false, 
          error: 'Style Profile ID is required',
          request_id: requestId,
          received_fields: Object.keys(body)
        },
        { status: 400 }
      );
    }
    
    // 🔍 ADD THIS DEBUG LOGGING
    console.log('✅ [DEBUG] Validation passed:', {
      template: body.template,
      style_profile: body.style_profile
    });
    
    // Validate backend URL
    if (!FASTAPI_BASE_URL) {
      console.error('🚨 [CONFIG] FASTAPI_BASE_URL not configured');
      return NextResponse.json(
        { 
          success: false, 
          error: 'Backend service not configured',
          request_id: requestId,
          debug_info: {
            fastapi_base_url: FASTAPI_BASE_URL,
            env_vars_available: Object.keys(process.env).filter(key => key.includes('FASTAPI'))
          }
        },
        { status: 503 }
      );
    }
    
    // Enterprise payload transformation
    const enterprisePayload = {
      requestId: requestId,
      template: body.template,
      style_profile: body.style_profile,
      topic: body.topic || body.dynamic_parameters?.topic || body.templateId || 'Future of LLMs',
      audience: body.audience || body.dynamic_parameters?.audience || 'general',
      platform: body.platform || body.dynamic_parameters?.platform || 'blog',
      length: body.length || body.dynamic_parameters?.length || 'medium',
      tags: body.tags || body.dynamic_parameters?.tags || [],
      tone: body.tone || body.dynamic_parameters?.tone || 'professional',
      code: body.code || body.dynamic_parameters?.code || false,
      dynamic_parameters: body.dynamic_parameters || {},
      priority: body.priority || 1,
      timeout_seconds: body.timeout_seconds || 300,
      generation_mode: body.generation_mode || "standard",
      created_at: new Date().toISOString(),
      user_id: body.user_id
    };
    
    // 🔍 ADD THIS DEBUG LOGGING
    console.log('🔍 [DEBUG] Final payload to backend:', JSON.stringify(enterprisePayload, null, 2));
    console.log('🔍 [DEBUG] Backend URL:', `${FASTAPI_BASE_URL}/api/generate`);
    
    // Rest of your existing code...
    // Continue with the fetch logic
    
  } catch (error: unknown) {
    const errorObj = error instanceof Error ? error : new Error(String(error));
    console.error('❌ [DEBUG] Request processing error:', errorObj.message);
    console.error('❌ [DEBUG] Full error:', errorObj);
    
    return NextResponse.json(
      { 
        success: false,
        error: 'Critical generation failure', 
        message: errorObj.message,
        request_id: requestId
      }, 
      { status: 500 }
    );
  }
}