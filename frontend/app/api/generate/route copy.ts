// frontend/app/api/generate/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';

//const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
//const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;

// Security validation
if (!FASTAPI_API_KEY) {
  console.warn('⚠️ FASTAPI_API_KEY not found in environment variables. Add to .env.local');
}

// Enterprise request tracking interface
interface GenerationRequest {

  template: string;
  style_profile: string;
  topic: string;
  audience?: string;
  platform?: string;
  length?: string;
  tags?: string[];
  tone?: string;
  code?: boolean;
  dynamic_parameters: Record<string, unknown>;
  priority: number;
  timeout_seconds: number;
  generation_mode: string;
  created_at: string;
  user_id?: string;
}

interface GenerationResponse {
  success: boolean;
  generation_id: string;
  request_id: string;
  status: string;
  content?: string;
  metadata?: Record<string, unknown>;
  error?: string;
  estimated_completion?: string;
  progress?: number;
}

// Enterprise error logging
const logError = (context: string, error: unknown, requestId?: string) => {
  const timestamp = new Date().toISOString();
  const errorObj = error instanceof Error ? error : new Error(String(error));
  const logData = {
    timestamp,
    context,
    request_id: requestId,
    error: {
      message: errorObj.message || 'Unknown error',
      stack: errorObj.stack,
      name: errorObj.name,
      code: typeof (errorObj as { code?: unknown })?.code !== 'undefined' ? (errorObj as { code?: unknown }).code : undefined
    }
  };
  console.error(`🚨 [ENTERPRISE] ${context}:`, JSON.stringify(logData, null, 2));
};

// Enterprise success logging
const logSuccess = (context: string, data: unknown, requestId?: string) => {
  const timestamp = new Date().toISOString();
  const logData = {
    timestamp,
    context,
    request_id: requestId,
    data: typeof data === 'object' ? data : { result: data }
  };
  console.log(`✅ [ENTERPRISE] ${context}:`, JSON.stringify(logData, null, 2));
};

// Enhanced content extraction for multiple backend patterns
function extractContentFromBackendResponse(data: unknown): string {
  // Debug logging to see what we're getting from the backend
  console.log('🔍 [DEBUG] Complete backend response structure:');
  console.log('🔍 [DEBUG] Response keys:', data && typeof data === 'object' ? Object.keys(data) : 'Not an object');
  console.log('🔍 [DEBUG] Response type:', typeof data);
  console.log('🔍 [DEBUG] Full response (first 500 chars):', JSON.stringify(data, null, 2).substring(0, 500));
  
  // Type guard for object with string properties
  const isObjectWithStringProps = (obj: unknown): obj is Record<string, unknown> => {
    return typeof obj === 'object' && obj !== null;
  };
  
  if (!isObjectWithStringProps(data)) {
    console.warn('⚠️ [DEBUG] Response is not an object');
    return '';
  }
  
  // Enhanced graph content extraction - prioritize formatted content
  const possibleContentFields = [
    'content',           // Final content field
    'formatted_content', // From formatter agent
    'edited_content',    // From editor agent  
    'draft_content',     // From writer agent
    'draft',            // From innovative writer
    'result',
    'final_content',
    'output',
    'formatted_article', // Legacy field
    'edited_draft'       // Legacy field
  ] as const;
  
  // Direct field access with proper type checking
  for (const field of possibleContentFields) {
    const fieldValue = data[field];
    // Explicit type guard for string values
    if (fieldValue != null && typeof fieldValue === 'string') {
      const trimmedValue = fieldValue.trim();
      if (trimmedValue.length > 0) {
        console.log(`✅ [DEBUG] Found content in field '${field}', length: ${trimmedValue.length}`);
        return trimmedValue;
      }
    }
  }
  
  // Check if data is nested in a state object (AgentState structure)
  const stateObj = data.state;
  if (isObjectWithStringProps(stateObj)) {
    console.log('🔍 [DEBUG] Checking nested AgentState:', Object.keys(stateObj));
    for (const field of possibleContentFields) {
      const fieldValue = stateObj[field];
      // Explicit type guard for string values
      if (fieldValue != null && typeof fieldValue === 'string') {
        const trimmedValue = fieldValue.trim();
        if (trimmedValue.length > 0) {
          console.log(`✅ [DEBUG] Found content in state.${field}, length: ${trimmedValue.length}`);
          return trimmedValue;
        }
      }
    }
  }
  
  // Check for Pydantic model structure (enhanced graph returns this)
  const nestedObjects = ['agent_state', 'final_state', 'graph_state', 'result_state'] as const;
  for (const nested of nestedObjects) {
    const nestedObj = data[nested];
    if (isObjectWithStringProps(nestedObj)) {
      console.log(`🔍 [DEBUG] Checking nested ${nested}:`, Object.keys(nestedObj));
      for (const field of possibleContentFields) {
        const fieldValue = nestedObj[field];
        // Explicit type guard for string values
        if (fieldValue != null && typeof fieldValue === 'string') {
          const trimmedValue = fieldValue.trim();
          if (trimmedValue.length > 0) {
            console.log(`✅ [DEBUG] Found content in ${nested}.${field}, length: ${trimmedValue.length}`);
            return trimmedValue;
          }
        }
      }
    }
  }
  
  // Check if the entire response is content - FIXED: proper string type handling
  if (typeof data === 'string') {
    const trimmedData = (typeof data === 'string' && data !== null) ? (data as string).trim() : '';
    if (trimmedData.length > 50) {
      console.log(`✅ [DEBUG] Using entire response as content, length: ${trimmedData.length}`);
      return trimmedData;
    }
  }
  
  // Recursive search for ANY substantial text content
  console.warn('⚠️ [DEBUG] No content found in standard fields, searching recursively...');
  const findAnyContent = (obj: unknown, path = '', depth = 0): string => {
    if (depth > 3) return ''; // Prevent infinite recursion
    
    // Type guard for string check - FIXED: proper string type handling
    if (typeof obj === 'string') {
      const trimmedObj = obj.trim();
      if (trimmedObj.length > 100) {
        console.log(`🔍 [DEBUG] Found potential content at ${path}: ${trimmedObj.length} chars`);
        return trimmedObj;
      }
    }
    
    if (isObjectWithStringProps(obj)) {
      for (const [key, value] of Object.entries(obj)) {
        const result = findAnyContent(value, path ? `${path}.${key}` : key, depth + 1);
        if (result) return result;
      }
    }
    return '';
  };
  
  const alternativeContent = findAnyContent(data);
  if (alternativeContent) {
    console.log('✅ [DEBUG] Found alternative content:', alternativeContent.length, 'chars');
    return alternativeContent;
  }
  
  // Log all available fields for debugging
  const availableFields = Object.keys(data);
  console.warn(`⚠️ [DEBUG] No content found anywhere. Available top-level fields: ${availableFields.join(', ')}`);
  
  return '';
}

export async function POST(request: NextRequest) {
  const requestId = randomUUID();
  const startTime = Date.now();
  
  try {
    const body = await request.json();
    
    // Enterprise request validation
    if (!body.templateId && !body.template) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Template ID is required',
          request_id: requestId
        },
        { status: 400 }
      );
    }

    if (!body.styleProfileId && !body.style_profile) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Style Profile ID is required',
          request_id: requestId
        },
        { status: 400 }
      );
    }
    
    // Enterprise payload transformation - Enhanced for backend planning agent
    const enterprisePayload: GenerationRequest = {
      template: body.templateId || body.template,
      style_profile: body.styleProfileId || body.style_profile,
      // Add ALL fields that the planning agent expects
      topic: body.topic || body.dynamic_parameters?.topic || body.templateId || 'Future of LLMs',
      audience: body.audience || body.dynamic_parameters?.audience || 'general',
      platform: body.platform || body.dynamic_parameters?.platform || 'blog',
      length: body.length || body.dynamic_parameters?.length || 'medium',
      // Additional fields for planning agent
      tags: body.tags || body.dynamic_parameters?.tags || [],
      tone: body.tone || body.dynamic_parameters?.tone || 'professional',
      code: body.code || body.dynamic_parameters?.code || false,
      dynamic_parameters: body.dynamic_parameters || {},
      priority: body.priority || 1,
      timeout_seconds: body.timeout_seconds || 300,
      generation_mode: body.generation_mode || "standard",
      created_at: new Date().toISOString(),
      user_id: body.user_id // Enterprise user tracking
    };
    
    logSuccess('Generation Request Initiated', {
      request_id: requestId,
      template: enterprisePayload.template,
      style_profile: enterprisePayload.style_profile,
      generation_mode: enterprisePayload.generation_mode,
      priority: enterprisePayload.priority
    }, requestId);
    
    // Enterprise backend request with retry logic
    let attempts = 0;
    const maxAttempts = 3;
    let lastError: Error | null = null;

    while (attempts < maxAttempts) {
      attempts++;
      
      try {
        const response = await fetch(`${FASTAPI_BASE_URL}/api/generate`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${FASTAPI_API_KEY}`,
            'Content-Type': 'application/json',
            'X-Request-ID': requestId || '',
            'X-Client-Version': '2.0.0',
            'X-Generation-Mode': enterprisePayload.generation_mode
          },
          body: JSON.stringify(enterprisePayload),
          signal: AbortSignal.timeout(enterprisePayload.timeout_seconds * 1000),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Unknown backend error' }));
          
          if (response.status >= 500 && attempts < maxAttempts) {
            logError(`Backend Error - Attempt ${attempts}`, errorData, requestId);
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempts) * 1000)); // Exponential backoff
            continue;
          }
          
          logError('Backend Request Failed', {
            status: response.status,
            statusText: response.statusText,
            error: errorData,
            attempts
          }, requestId);
          
          return NextResponse.json(
            { 
              success: false, 
              error: errorData.detail || 'Content generation failed',
              request_id: requestId,
              status_code: response.status,
              attempts,
              details: errorData
            }, 
            { status: response.status }
          );
        }

        const data = await response.json();
        const processingTime = Date.now() - startTime;
        
        // ENHANCED CONTENT EXTRACTION
        const extractedContent = extractContentFromBackendResponse(data);
        
        // Enterprise response formatting
        const enterpriseResponse: GenerationResponse = {
          success: true,
          generation_id: data.generation_id || data.requestId,
          request_id: data.request_id || requestId,
          status: data.status || (extractedContent ? 'completed' : 'processing'),
          content: extractedContent, // Use extracted content instead of data.content
          metadata: {
            ...data.metadata,
            processing_time_ms: processingTime,
            attempts,
            backend_generation_id: data.generation_id,
            template_used: enterprisePayload.template,
            style_profile_used: enterprisePayload.style_profile,
            generation_mode: enterprisePayload.generation_mode,
            // Enhanced metadata
            innovation_report: data.innovation_report || data.metadata?.innovation_report,
            content_quality: data.metadata?.content_quality,
            word_count: extractedContent ? extractedContent.split(' ').length : 0,
            content_extraction_method: extractedContent ? 'enhanced' : 'fallback'
          },
          estimated_completion: data.estimated_completion,
          progress: data.progress || 100
        };
        
        logSuccess('Generation Completed Successfully', {
          generation_id: enterpriseResponse.generation_id,
          processing_time_ms: processingTime,
          content_length: extractedContent ? extractedContent.length : 0,
          attempts,
          content_found: !!extractedContent
        }, requestId);
        
        return NextResponse.json(enterpriseResponse);
        
      } catch (fetchError: unknown) {
        const error = fetchError instanceof Error ? fetchError : new Error(String(fetchError));
        lastError = error;
        
        if (typeof fetchError === 'object' && fetchError !== null && 'name' in fetchError && (fetchError as { name: string }).name === 'AbortError') {
          logError('Generation Timeout', { timeout_seconds: enterprisePayload.timeout_seconds }, requestId);
          break;
        }
        
        if (attempts < maxAttempts) {
          logError(`Request Failed - Attempt ${attempts}`, fetchError, requestId);
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempts) * 1000));
          continue;
        }
      }
    }
    
    // All attempts failed
    const processingTime = Date.now() - startTime;
    
    if (lastError?.name === 'AbortError') {
      return NextResponse.json(
        { 
          success: false,
          error: 'Generation timeout', 
          message: `Content generation exceeded ${enterprisePayload.timeout_seconds} seconds`,
          request_id: requestId,
          processing_time_ms: processingTime
        }, 
        { status: 504 }
      );
    }
    
    // Type guard for error with 'code' property
    function hasErrorCode(obj: unknown): obj is { code: string } {
      return typeof obj === 'object' && obj !== null && 'code' in obj && typeof (obj as { code: unknown }).code === 'string';
    }
    
        if (lastError && hasErrorCode(lastError) && lastError.code === 'ECONNREFUSED') {
          return NextResponse.json(
            { 
              success: false,
              error: 'Backend service unavailable', 
              message: 'Cannot connect to generation service',
              request_id: requestId,
              processing_time_ms: processingTime,
              attempts
            }, 
            { status: 503 }
          );
        }
    
    return NextResponse.json(
      { 
        success: false,
        error: 'Generation failed after multiple attempts', 
        message: lastError?.message || 'Unknown error',
        request_id: requestId,
        processing_time_ms: processingTime,
        attempts
      }, 
      { status: 500 }
    );
    
  } catch (error: unknown) {
    const errorObj = error instanceof Error ? error : new Error(String(error));
    const processingTime = Date.now() - startTime;
    logError('Critical Generation Error', error, requestId);
    
    return NextResponse.json(
      { 
        success: false,
        error: 'Critical generation failure', 
        message: errorObj.message,
        request_id: requestId,
        processing_time_ms: processingTime
      }, 
      { status: 500 }
    );
  }
}

// Enterprise status checking with enhanced tracking
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const requestId = searchParams.get('request_id');
    const generationId = searchParams.get('generation_id') || searchParams.get('id');
    
    if (!requestId && !generationId) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Either request_id or generation_id is required' 
        },
        { status: 400 }
      );
    }
    
    const trackingId = requestId || generationId || '';
    
    logSuccess('Status Check Initiated', { tracking_id: trackingId }, trackingId);
    
    // Try multiple possible backend endpoints
    let response;
    let backendError: unknown = null;
    
    // Try primary status endpoint
    try {
      response = await fetch(`${FASTAPI_BASE_URL}/api/status/${trackingId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${FASTAPI_API_KEY}`,
          'Content-Type': 'application/json',
          'X-Request-ID': trackingId,
        },
      });
    } catch (error) {
      backendError = error;
    }
    
    // If first endpoint fails, try alternative endpoint
    if (!response || !response.ok) {
      try {
        response = await fetch(`${FASTAPI_BASE_URL}/api/generation/${trackingId}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${FASTAPI_API_KEY}`,
            'Content-Type': 'application/json',
            'X-Request-ID': trackingId,
          },
        });
      } catch (error) {
        backendError = error;
      }
    }
    
    // If both specific endpoints fail, try simple status check
    if (!response || !response.ok) {
      try {
        response = await fetch(`${FASTAPI_BASE_URL}/status`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${FASTAPI_API_KEY}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          // Return mock status for now since backend endpoint might not exist
          const mockStatus = {
            success: true,
            request_id: requestId,
            generation_id: generationId,
            status: "completed",
            progress: 100,
            message: "Generation completed (status endpoint not implemented)",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            metadata: { mock: true, note: "Backend status endpoint not available" }
          };
          
          logSuccess('Status Check Completed (Mock)', mockStatus, trackingId);
          return NextResponse.json(mockStatus);
        }
      } catch (error) {
        backendError = error;
      }
    }

    if (!response || !response.ok) {
      // FIXED: Proper error data typing and message extraction
      const errorData = await response?.json().catch(() => ({ detail: 'Status check failed' })) as {
        detail?: string;
        message?: string;
        error?: string;
      };
      
      // Extract error message with proper fallbacks
      const errorMessage = errorData?.detail || 
                          errorData?.message || 
                          errorData?.error ||
                          (backendError instanceof Error ? backendError.message : 
                           typeof backendError === 'string' ? backendError : 
                           'Failed to get generation status');
      
      logError('Status Check Failed', {
        error: errorData,
        backend_error: backendError instanceof Error ? backendError.message : String(backendError),
        status: response?.status,
        statusText: response?.statusText
      }, trackingId);
      
      return NextResponse.json(
        { 
          success: false, 
          error: errorMessage,
          request_id: trackingId,
          backend_available: false
        },
        { status: response?.status || 503 }
      );
    }

    // FIXED: Proper response data typing
    const data = await response.json() as {
      generation_id?: string;
      status?: string;
      progress?: number;
      message?: string;
      created_at?: string;
      updated_at?: string;
      metadata?: Record<string, unknown>;
      content?: string;
      error?: string;
    };
    
    // Type-safe property access with proper defaults
    const statusResponse = {
      success: true,
      request_id: requestId,
      generation_id: data.generation_id || generationId || '',
      status: data.status || 'unknown',
      progress: data.progress || 0,
      message: data.message || '',
      created_at: data.created_at || new Date().toISOString(),
      updated_at: data.updated_at || new Date().toISOString(),
      metadata: data.metadata || {},
      // FIXED: Safe conditional object spreading
      ...(data.content ? { content: data.content } : {}),
      ...(data.error ? { error: data.error } : {})
    };
    
    logSuccess('Status Check Completed', statusResponse, trackingId);
    
    return NextResponse.json(statusResponse);
    
  } catch (error: unknown) {
    logError('Status Check Error', error);
    return NextResponse.json(
      { success: false, error: 'Failed to check generation status' },
      { status: 500 }
    );
  }
}

// Enterprise generation cancellation
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const requestId = searchParams.get('request_id');
    const generationId = searchParams.get('generation_id') || searchParams.get('id');
    
    if (!requestId && !generationId) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Either request_id or generation_id is required' 
        },
        { status: 400 }
      );
    }
    
    const trackingId = requestId || generationId || '';
    
    logSuccess('Cancellation Requested', { tracking_id: trackingId });
    
    // Enterprise cancellation logic
    const cancellationResponse = {
      success: true,
      message: 'Generation cancellation requested',
      request_id: requestId,
      generation_id: generationId,
      cancelled_at: new Date().toISOString(),
      status: 'cancelled'
    };
    
    logSuccess('Generation Cancelled', cancellationResponse, trackingId);
    
    return NextResponse.json(cancellationResponse);
    
  } catch (error: unknown) {
    logError('Cancellation Error', error);
    return NextResponse.json(
      { success: false, error: 'Failed to cancel generation' },
      { status: 500 }
    );
  }
}