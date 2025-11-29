// frontend/app/api/generate/route.ts
// FIXED: Remove polling, fix request_id undefined issue

import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';


const API_BASE_URL =
  process.env.FASTAPI_BASE_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";

const API_KEY =
  process.env.FASTAPI_API_KEY ||
  process.env.LANGGRAPH_API_KEY ||
  process.env.NEXT_PUBLIC_LANGGRAPH_API_KEY;

if (!API_KEY) {
  console.warn("⚠️ No API key found. Add LANGGRAPH_API_KEY to .env.local");
}

const FASTAPI_BASE_URL = API_BASE_URL;
const FASTAPI_API_KEY = API_KEY;

interface GenerationRequest {
  request_id?: string; // Optional - backend generates if not provided
  template: string;
  style_profile: string;
  topic: string;
  audience?: string;
  platform?: string;
  length?: string;
  tags?: string[];
  tone?: string;
  code?: boolean;
  user_input?: Record<string, unknown>;
  dynamic_parameters: Record<string, unknown>;
  priority: number;
  timeout_seconds: number;
  generation_mode: string;
  created_at: string;
  user_id?: string;
}


interface BackendResponse {
  data?: {
    request_id?: string;
    status?: string;
    metadata?: Record<string, unknown>;
    content?: string;
  };
  request_id?: string;
  generation_id?: string;
  status?: string;
  metadata?: Record<string, unknown>;
  estimated_completion?: string;
  progress?: number;
  content?: string;
}


function generateTopicFromTemplate(template: string, styleProfile: string, providedTopic?: string): string {
  if (providedTopic && providedTopic.trim().length > 0) {
    return providedTopic.trim();
  }
  
  const templateName = template.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
  const styleName = styleProfile.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
  
  if (template.includes('business_proposal')) {
    return `Strategic Business Proposal in ${styleName} approach`;
  } else if (template.includes('technical_documentation')) {
    return `Technical Documentation with ${styleName} style`;
  } else if (template.includes('social_media_campaign')) {
    return `Social Media Campaign using ${styleName} voice`;
  } else if (template.includes('blog_article')) {
    return `Blog Article: ${styleName} perspective`;
  } else if (template.includes('newsletter')) {
    return `Newsletter content in ${styleName} format`;
  } else {
    return `${templateName} content using ${styleName} approach`;
  }
}

const logError = (context: string, error: unknown, request_id?: string) => {
  const timestamp = new Date().toISOString();
  const errorObj = error instanceof Error ? error : new Error(String(error));
  const logData = {
    timestamp,
    context,
    frontend_request_id: request_id,
    error: {
      message: errorObj.message || 'Unknown error',
      stack: errorObj.stack,
      name: errorObj.name,
      code: typeof (errorObj as { code?: unknown })?.code !== 'undefined' ? (errorObj as { code?: unknown }).code : undefined
    }
  };
  console.error(`🚨 [ENTERPRISE] ${context}:`, JSON.stringify(logData, null, 2));
};

const logSuccess = (context: string, data: unknown, request_id?: string) => {
  const timestamp = new Date().toISOString();
  const logData = {
    timestamp,
    context,
    frontend_request_id: request_id,
    data: typeof data === 'object' ? data : { result: data }
  };
  console.log(`✅ [ENTERPRISE] ${context}:`, JSON.stringify(logData, null, 2));
};

const createFetchHeaders = (request_id: string, generationMode: string): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Request-ID': request_id || '',
    'X-Client-Version': '2.0.0',
    'X-Generation-Mode': generationMode
  };

  if (FASTAPI_API_KEY) {
    headers['Authorization'] = `Bearer ${FASTAPI_API_KEY}`;
  }

  return headers;
};

const categorizeFetchError = (error: Error): string => {
  const errorName = error.name.toLowerCase();
  const errorMessage = error.message.toLowerCase();
  
  if (errorName === 'aborterror' || errorMessage.includes('abort')) {
    return 'ABORT';
  }
  
  if (errorMessage.includes('timeout')) {
    return 'TIMEOUT';
  }
  
  if (errorMessage.includes('network') || 
      errorMessage.includes('fetch') ||
      errorMessage.includes('econnrefused') ||
      errorMessage.includes('enotfound') ||
      errorMessage.includes('etimedout')) {
    return 'NETWORK';
  }
  
  if (errorMessage.includes('ssl') || 
      errorMessage.includes('tls') ||
      errorMessage.includes('certificate')) {
    return 'SSL';
  }
  
  if (errorMessage.includes('dns') || 
      errorMessage.includes('resolve') ||
      errorMessage.includes('enotfound')) {
    return 'DNS';
  }
  
  return 'UNKNOWN';
};

const performFetchWithRetry = async (
  url: string,
  payload: GenerationRequest,
  maxAttempts: number = 3
): Promise<Response> => {
  let lastError: Error | null = null;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), payload.timeout_seconds * 500);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: createFetchHeaders(payload.request_id || '', payload.generation_mode),
        body: JSON.stringify(payload),
        signal: controller.signal,
        keepalive: true,
        cache: 'no-cache',
        redirect: 'follow'
      });

      clearTimeout(timeoutId);
      
      console.log(`✅ [FETCH] Connected to backend (attempt ${attempt}/${maxAttempts})`);
      
      return response;
      
    } catch (fetchError: unknown) {
      const error = fetchError instanceof Error ? fetchError : new Error(String(fetchError));
      lastError = error;
      
      const errorCategory = categorizeFetchError(error);
      
      console.error(`❌ [FETCH] Attempt ${attempt}/${maxAttempts} failed:`, {
        category: errorCategory,
        message: error.message,
        name: error.name,
        stack: error.stack?.split('\n').slice(0, 3).join('\n')
      });
      
      if (errorCategory === 'TIMEOUT' || errorCategory === 'ABORT') {
        console.warn(`⚠️ [FETCH] ${errorCategory} error - not retrying`);
        break;
      }
      
      if (attempt < maxAttempts && errorCategory === 'NETWORK') {
        const backoffMs = Math.pow(2, attempt) * 1000;
        console.log(`⏳ [FETCH] Retrying in ${backoffMs}ms...`);
        await new Promise(resolve => setTimeout(resolve, backoffMs));
        continue;
      }
    }
  }
  
  if (lastError) {
    throw lastError;
  }
  
  throw new Error('Fetch failed after all attempts');
};


export async function POST(request: NextRequest) {
  const frontend_request_id = randomUUID(); // For frontend tracking only
  const startTime = Date.now();
  
  try {
    const body = await request.json();
    // 🔍 DEBUG: Log incoming request
  console.log('🔍 [GENERATE-API] Request body:', JSON.stringify({
    has_template: !!body.template,
    has_templateId: !!body.templateId,
    has_style_profile: !!body.style_profile,
    has_styleProfileId: !!body.styleProfileId,
    has_generation_settings: !!body.generation_settings,
    generation_settings: body.generation_settings,
    keys: Object.keys(body)
  }, null, 2));
    
    if (!body.template && !body.templateId) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Template ID is required (use "template" or "templateId" field)',
          request_id: frontend_request_id,
          available_templates: ['business_proposal', 'technical_documentation', 'social_media_campaign', 'blog_article_generator', 'email_newsletter', 'press_release']
        },
        { status: 400 }
      );
    }
    
    if (!body.style_profile && !body.styleProfileId) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Style Profile ID is required (use "style_profile" or "styleProfileId" field)',
          request_id: frontend_request_id,
          available_styles: ['popular_sci', 'phd_academic', 'technical_dive', 'beginner_friendly', 'experimental_lab_log', 'phd_lit_review']
        },
        { status: 400 }
      );
    }
    
    const templateId = body.template || body.templateId;
    const styleProfileId = body.style_profile || body.styleProfileId;
    
    const generatedTopic = generateTopicFromTemplate(
      templateId, 
      styleProfileId, 
      body.topic || body.dynamic_parameters?.topic
    );
    
    console.log(`🎯 [GENERATION] Template: '${templateId}', Style: '${styleProfileId}', Topic: '${generatedTopic}'`);
  
    const generationSettings = body.generation_settings || {};
    const maxTokens = generationSettings.max_tokens;
    const temperature = generationSettings.temperature;
    const qualityMode = generationSettings.quality_mode;  

    if (!maxTokens || temperature === undefined || temperature === null || !qualityMode) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Generation settings required: max_tokens, temperature, quality_mode',
          request_id: frontend_request_id
        },
        { status: 400 }
      );
    }

    // ✅ FIX: Don't send frontend request_id - let backend generate its own
    const enterprisePayload: GenerationRequest = {
      // request_id removed - backend will generate
      template: templateId,
      style_profile: styleProfileId,
      topic: generatedTopic,
      audience: body.audience || body.dynamic_parameters?.audience || 'general',
      platform: body.platform || body.dynamic_parameters?.platform || 'blog',
      length: body.length || body.dynamic_parameters?.length || 'medium',
      tags: body.tags || body.dynamic_parameters?.tags || [],
      tone: body.tone || body.dynamic_parameters?.tone || 'professional',
      code: body.code || body.dynamic_parameters?.code || false,
      
      user_input: {
        topic: generatedTopic,
        ...body.dynamic_parameters,
        max_tokens: generationSettings.max_tokens,
        temperature: generationSettings.temperature,
        quality_mode: generationSettings.quality_mode,
      },
      
      dynamic_parameters: {
        dynamic_overrides: {
          api_name: body.dynamic_parameters?.api_name || "test",
          api_domain: body.dynamic_parameters?.api_domain || "web_service",
          auth_type: body.dynamic_parameters?.auth_type || "api_key",
          programming_languages: body.dynamic_parameters?.programming_languages || "",
          base_url: body.dynamic_parameters?.base_url || "",
          version_number: body.dynamic_parameters?.version_number || "v1",
          include_sdks: body.dynamic_parameters?.include_sdks !== undefined ? body.dynamic_parameters.include_sdks : true,
          include_postman: body.dynamic_parameters?.include_postman !== undefined ? body.dynamic_parameters.include_postman : true,
          complexity_level: body.dynamic_parameters?.complexity_level || "intermediate",
          min_endpoints: body.dynamic_parameters?.min_endpoints || "",
          code_examples_per_endpoint: body.dynamic_parameters?.code_examples_per_endpoint || "",
          include_webhooks: body.dynamic_parameters?.include_webhooks || "",
          rate_limiting: body.dynamic_parameters?.rate_limiting || "",
          max_tokens: generationSettings.max_tokens,
          temperature: generationSettings.temperature,
          quality_mode: generationSettings.quality_mode,
          preferred_length: body.dynamic_parameters?.preferred_length || "short",
          creativity_level: body.dynamic_parameters?.creativity_level || "focused",
          content_quality: body.dynamic_parameters?.content_quality || "fast",
          template_id: templateId,
          style_profile_id: styleProfileId,
          topic: generatedTopic,
          template_category: body.dynamic_parameters?.template_category || 'general',
          style_tone: body.dynamic_parameters?.style_tone || 'professional',
          content_structure: body.dynamic_parameters?.content_structure || 'standard',
          audience: body.audience || body.dynamic_parameters?.audience || 'general',
          platform: body.platform || body.dynamic_parameters?.platform || 'blog',
          length: body.length || body.dynamic_parameters?.length || 'medium',
          tone: body.tone || body.dynamic_parameters?.tone || 'professional',
        },
        ...body.dynamic_parameters,
        template_id: templateId,
        style_profile_id: styleProfileId,
        topic: generatedTopic,
      },
      
      priority: body.priority || 1,
      timeout_seconds: body.timeout_seconds || 600,
      generation_mode: body.generation_mode || "enhanced",
      created_at: new Date().toISOString(),
      user_id: body.user_id
    };
    
    if (!FASTAPI_BASE_URL) {
      console.error('🚨 [CONFIG] FASTAPI_BASE_URL not configured');
      return NextResponse.json(
        { 
          success: false, 
          error: 'Backend service not configured',
          request_id: frontend_request_id
        },
        { status: 503 }
      );
    }
    
    logSuccess('Generation Request Initiated', {
      frontend_request_id: frontend_request_id,
      template: enterprisePayload.template,
      style_profile: enterprisePayload.style_profile,
      topic: enterprisePayload.topic,
      generation_mode: enterprisePayload.generation_mode,
      priority: enterprisePayload.priority,
      backend_url: FASTAPI_BASE_URL,
      has_api_key: !!FASTAPI_API_KEY
    }, frontend_request_id);
    
    try {
      const response = await performFetchWithRetry(
        `${FASTAPI_BASE_URL}/api/generate`,
        enterprisePayload,
        3
      );
      
      if (!response.ok) {
        let errorData: { detail?: string; message?: string; error?: string } = { detail: 'Unknown backend error' };
        
        try {
          const contentType = response.headers.get('content-type');
          if (contentType?.includes('application/json')) {
            errorData = await response.json();
          } else {
            const textData = await response.text();
            errorData = { detail: `Backend returned non-JSON response: ${textData.substring(0, 200)}` };
          }
        } catch {
          errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
        }
        
        logError('Backend HTTP Error', {
          status: response.status,
          statusText: response.statusText,
          error: errorData,
          content_type: response.headers.get('content-type'),
          content_length: response.headers.get('content-length')
        }, frontend_request_id);
        
        return NextResponse.json(
          { 
            success: false, 
            error: errorData.detail || errorData.message || errorData.error || 'Content generation failed',
            request_id: frontend_request_id,
            status_code: response.status,
            details: errorData
          }, 
          { status: response.status }
        );
      }
      
      let data: BackendResponse;
      try {
        const contentType = response.headers.get('content-type');
        if (contentType?.includes('application/json')) {
          data = await response.json();
        } else {
          const textData = await response.text();
          console.warn('⚠️ [RESPONSE] Non-JSON response received:', textData.substring(0, 200));
          data = { content: textData } as BackendResponse;
        }
      } catch {
        return NextResponse.json(
          { 
            success: false, 
            error: 'Failed to parse backend response',
            request_id: frontend_request_id
          },
          { status: 502 }
        );
      }
      
      // ✅ FIX: Extract backend's actual request_id
      const finalData = data; // Rename for compatibility with rest of code
      const backendRequestId = finalData?.data?.request_id || finalData?.request_id || finalData?.generation_id || frontend_request_id;      
      // Return 202 immediately - client polls via status endpoint
      return NextResponse.json({
        success: true,
        request_id: backendRequestId,
        generation_id: backendRequestId,
        status: 'pending',
        message: 'Generation started in background'
      }, { status: 202 });
      
    } catch (fetchError: unknown) {
      const error = fetchError instanceof Error ? fetchError : new Error(String(fetchError));
      const processingTime = Date.now() - startTime;
      const errorCategory = categorizeFetchError(error);
      
      logError('Fetch Operation Failed', {
        error_category: errorCategory,
        error_name: error.name,
        error_message: error.message,
        processing_time_ms: processingTime,
        backend_url: FASTAPI_BASE_URL,
        timeout_seconds: enterprisePayload.timeout_seconds,
        template: enterprisePayload.template,
        style_profile: enterprisePayload.style_profile
      }, frontend_request_id);
      
      switch (errorCategory) {
        case 'TIMEOUT':
        case 'ABORT':
          return NextResponse.json(
            { 
              success: false,
              error: 'Generation timeout', 
              message: `Content generation exceeded ${enterprisePayload.timeout_seconds} seconds`,
              request_id: frontend_request_id,
              processing_time_ms: processingTime
            }, 
            { status: 504 }
          );
          
        case 'NETWORK':
        case 'DNS':
          return NextResponse.json(
            { 
              success: false,
              error: 'Backend service unavailable', 
              message: 'Cannot connect to generation service',
              request_id: frontend_request_id,
              processing_time_ms: processingTime,
              details: {
                backend_url: FASTAPI_BASE_URL,
                error_type: errorCategory,
                error_message: error.message
              }
            }, 
            { status: 503 }
          );
          
        case 'SSL':
          return NextResponse.json(
            { 
              success: false,
              error: 'SSL connection failed', 
              message: 'Secure connection to backend failed',
              request_id: frontend_request_id,
              processing_time_ms: processingTime
            }, 
            { status: 502 }
          );
          
        default:
          return NextResponse.json(
            { 
              success: false,
              error: 'Generation failed', 
              message: error.message || 'Unknown error occurred',
              request_id: frontend_request_id,
              processing_time_ms: processingTime
            }, 
            { status: 500 }
          );
      }
    }
    
  } catch (error: unknown) {
    const errorObj = error instanceof Error ? error : new Error(String(error));
    const processingTime = Date.now() - startTime;
    logError('Critical Generation Error', error, frontend_request_id);
    
    return NextResponse.json(
      { 
        success: false,
        error: 'Critical generation failure', 
        message: errorObj.message,
        request_id: frontend_request_id,
        processing_time_ms: processingTime
      }, 
      { status: 500 }
    );
  }
}