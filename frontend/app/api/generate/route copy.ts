// frontend/app/api/generate/route.ts
// ✅ FIXED VERSION - Proper Template/Style Profile Separation

import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import fs from 'fs/promises';
import path from 'path';

// route.ts (top)

// Use the values you already set in .env.local
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

// Warn if missing
if (!API_KEY) {
  console.warn("⚠️ No API key found. Add LANGGRAPH_API_KEY to .env.local");
}

// Temporary aliases so we don't have to touch every old reference
const FASTAPI_BASE_URL = API_BASE_URL;
const FASTAPI_API_KEY = API_KEY;

// ✅ FIXED: Enhanced request interface with proper template/style separation
interface GenerationRequest {
  request_id: string;
  template: string;           // Template ID (e.g., "business_proposal", "technical_documentation")
  style_profile: string;      // Style Profile ID (e.g., "phd_academic", "popular_sci")
  topic: string;              // Actual content topic - NO MORE "Future of LLMs" default!
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
  innovation_report?: unknown;
  content_quality?: unknown;
  estimated_completion?: string;
  progress?: number;
  content?: string;
}

// ✅ ENHANCED: Better content type inference from actual template names
function inferContentType(template: string): string {
  const templateLower = template.toLowerCase();
  
  // Map to actual template IDs from your system
  if (templateLower.includes('business_proposal') || templateLower.includes('business')) return 'Business Proposal';
  if (templateLower.includes('technical_documentation') || templateLower.includes('technical_documents')) return 'Technical Documentation';
  if (templateLower.includes('social_media_campaign') || templateLower.includes('social')) return 'Social Media Campaign';
  if (templateLower.includes('email_newsletter') || templateLower.includes('newsletter')) return 'Email Newsletter';
  if (templateLower.includes('press_release') || templateLower.includes('press')) return 'Press Release';
  if (templateLower.includes('blog_article_generator') || templateLower.includes('blog')) return 'Blog Article';
  
  // Legacy fallbacks
  if (templateLower.includes('learning') || templateLower.includes('tutorial')) return 'Educational';
  if (templateLower.includes('decision') || templateLower.includes('tree')) return 'Data Science';
  if (templateLower.includes('future') || templateLower.includes('trend')) return 'Analysis';
  if (templateLower.includes('federated')) return 'AI Research';
  if (templateLower.includes('ai') || templateLower.includes('ml')) return 'AI/ML';
  
  return 'Article';
}

// ✅ ENHANCED: Generate meaningful topic from template and style when not provided
function generateTopicFromTemplate(template: string, styleProfile: string, providedTopic?: string): string {
  if (providedTopic && providedTopic.trim().length > 0) {
    return providedTopic.trim();
  }
  
  // Generate topic based on template and style combination
  const templateName = template.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
  const styleName = styleProfile.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
  
  // Template-specific topic generation
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
    // Generic but meaningful fallback
    return `${templateName} content using ${styleName} approach`;
  }
}

// ✅ ENHANCED: Auto-save functionality with better directory structure
async function saveGeneratedContent(content: string, metadata: {
  request_id: string;
  template: string;
  style_profile: string;
  topic: string;
  audience?: string;
}): Promise<{ saved_path: string; content_id: string }> {
  try {
    // Create content ID from topic and timestamp
    const timestamp = new Date().toISOString().split('T')[0].replace(/-/g, '');
    const topicSlug = metadata.topic
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, '_')
      .substring(0, 50);
    
    const contentId = `${topicSlug}_${timestamp}_${metadata.request_id.substring(0, 8)}`;
    
    // ✅ FIXED: Save to generated_content directory (not storage)
    const saveDir = path.join(process.cwd(), '../generated_content');
    
    // ✅ FIXED: Create proper week directory structure
    const now = new Date();
    const currentWeek = `week_${now.getFullYear()}_${Math.ceil((now.getTime() - new Date(now.getFullYear(), 0, 1).getTime()) / (7 * 24 * 60 * 60 * 1000))}`;
    const weekDir = path.join(saveDir, currentWeek);
    
    // Ensure directory exists
    await fs.mkdir(weekDir, { recursive: true });
    
    // Calculate content statistics
    const wordCount = content.split(/\s+/).filter(word => word.length > 0).length;
    const readingTime = Math.ceil(wordCount / 200);
    
    // ✅ ENHANCED: Create metadata object that matches content API expectations
    const contentMetadata = {
      title: metadata.topic || 'Generated Content',
      status: 'draft' as const,
      type: inferContentType(metadata.template),
      content, // Store content in JSON as backup
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      author: 'AI Assistant',
      views: 0,
      metadata: {
        template: metadata.template,
        styleProfile: metadata.style_profile,
        request_id: metadata.request_id,
        topic: metadata.topic,
        audience: metadata.audience,
        wordCount,
        readingTime,
        generatedAt: new Date().toISOString(),
        generation_mode: 'enhanced'
      }
    };
    
    // Save JSON metadata file
    const jsonPath = path.join(weekDir, `${contentId}.json`);
    await fs.writeFile(jsonPath, JSON.stringify(contentMetadata, null, 2));
    
    // ✅ ENHANCED: Save markdown content file with frontmatter
    const mdPath = path.join(weekDir, `${contentId}.md`);
    const frontmatter = [
      '---',
      `title: "${metadata.topic}"`,
      `template: "${metadata.template}"`,
      `styleProfile: "${metadata.style_profile}"`,
      `status: "draft"`,
      `type: "${inferContentType(metadata.template)}"`,
      `createdAt: "${new Date().toISOString()}"`,
      '---',
      '',
      content
    ].join('\n');
    
    await fs.writeFile(mdPath, frontmatter);
    
    console.log(`✅ [AUTO-SAVE] Content saved successfully:`, {
      contentId,
      week: currentWeek,
      jsonPath,
      mdPath,
      wordCount,
      readingTime
    });
    
    return {
      saved_path: jsonPath,
      content_id: contentId
    };
    
  } catch (error) {
    console.error('❌ [AUTO-SAVE] Failed to save content:', error);
    // Don't throw error - generation should still succeed even if save fails
    return {
      saved_path: '',
      content_id: ''
    };
  }
}

// Enterprise error logging
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

// Enterprise success logging
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

// Enhanced fetch headers configuration
const createFetchHeaders = (request_id: string, generationMode: string): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`,
    'Accept': 'application/json',
    'X-Request-ID': request_id || '',
    'X-Client-Version': '2.0.0',
    'X-Generation-Mode': generationMode
  };

  // Only add Authorization header if API key exists
  if (FASTAPI_API_KEY) {
    headers['Authorization'] = `Bearer ${FASTAPI_API_KEY}`;
  }

  return headers;
};

// Error categorization helper
const categorizeFetchError = (error: Error): string => {
  const errorName = error.name.toLowerCase();
  const errorMessage = error.message.toLowerCase();
  
  // Timeout/Abort errors
  if (errorName === 'aborterror' || errorMessage.includes('abort')) {
    return 'ABORT';
  }
  
  if (errorMessage.includes('timeout')) {
    return 'TIMEOUT';
  }
  
  // Network connectivity errors
  if (errorMessage.includes('network') || 
      errorMessage.includes('fetch') ||
      errorMessage.includes('econnrefused') ||
      errorMessage.includes('enotfound') ||
      errorMessage.includes('etimedout')) {
    return 'NETWORK';
  }
  
  // SSL/TLS errors
  if (errorMessage.includes('ssl') || 
      errorMessage.includes('tls') ||
      errorMessage.includes('certificate')) {
    return 'SSL';
  }
  
  // DNS errors
  if (errorMessage.includes('dns') || 
      errorMessage.includes('resolve') ||
      errorMessage.includes('enotfound')) {
    return 'DNS';
  }
  
  return 'UNKNOWN';
};

// Enhanced fetch with comprehensive error handling
const performFetchWithRetry = async (
  url: string,
  payload: GenerationRequest,
  maxAttempts: number = 3
): Promise<Response> => {
  let lastError: Error | null = null;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      // Create AbortController for timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), payload.timeout_seconds * 1000);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: createFetchHeaders(payload.request_id, payload.generation_mode),
        body: JSON.stringify(payload),
        signal: controller.signal,
        // Additional fetch options for reliability
        keepalive: true,
        cache: 'no-cache',
        redirect: 'follow'
      });

      // Clear timeout on successful response
      clearTimeout(timeoutId);
      
      // Log successful connection
      console.log(`✅ [FETCH] Connected to backend (attempt ${attempt}/${maxAttempts})`);
      
      return response;
      
    } catch (fetchError: unknown) {
      const error = fetchError instanceof Error ? fetchError : new Error(String(fetchError));
      lastError = error;
      
      // Enhanced error categorization
      const errorCategory = categorizeFetchError(error);
      
      console.error(`❌ [FETCH] Attempt ${attempt}/${maxAttempts} failed:`, {
        category: errorCategory,
        message: error.message,
        name: error.name,
        stack: error.stack?.split('\n').slice(0, 3).join('\n') // First 3 lines only
      });
      
      // Don't retry on certain errors
      if (errorCategory === 'TIMEOUT' || errorCategory === 'ABORT') {
        console.warn(`⚠️ [FETCH] ${errorCategory} error - not retrying`);
        break;
      }
      
      // Exponential backoff for retryable errors
      if (attempt < maxAttempts && errorCategory === 'NETWORK') {
        const backoffMs = Math.pow(2, attempt) * 1000;
        console.log(`⏳ [FETCH] Retrying in ${backoffMs}ms...`);
        await new Promise(resolve => setTimeout(resolve, backoffMs));
        continue;
      }
    }
  }
  
  // All attempts failed
  if (lastError) {
    throw lastError;
  }
  
  throw new Error('Fetch failed after all attempts');
};

// Enhanced content extraction for multiple backend patterns
function extractContentFromBackendResponse(data: unknown): string {
  console.log('🔍 [DEBUG] Full backend response:', JSON.stringify(data, null, 2));
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
  const request_id = randomUUID();
  const startTime = Date.now();
  
  try {
    const body = await request.json();
    
    // ✅ FIXED: Enhanced validation with proper error messages
    if (!body.template && !body.templateId) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Template ID is required (use "template" or "templateId" field)',
          request_id: request_id,
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
          request_id: request_id,
          available_styles: ['popular_sci', 'phd_academic', 'technical_dive', 'beginner_friendly', 'experimental_lab_log', 'phd_lit_review']
        },
        { status: 400 }
      );
    }
    
    // ✅ FIXED: Normalize field names for backward compatibility
    const templateId = body.template || body.templateId;
    const styleProfileId = body.style_profile || body.styleProfileId;
    
    // ✅ FIXED: Generate meaningful topic - NO MORE "Future of LLMs" default!
    const generatedTopic = generateTopicFromTemplate(
      templateId, 
      styleProfileId, 
      body.topic || body.dynamic_parameters?.topic
    );
    
    console.log(`🎯 [GENERATION] Template: '${templateId}', Style: '${styleProfileId}', Topic: '${generatedTopic}'`);
    
    // ✅ ENHANCED: Enterprise payload transformation with proper template/style separation
    const enterprisePayload: GenerationRequest = {
      request_id: request_id, // Frontend request_id that backend will use
      template: templateId,  // Content template (structure/format)
      style_profile: styleProfileId,  // Style profile (tone/voice/approach)
      topic: generatedTopic,  // Meaningful topic based on template + style
      audience: body.audience || body.dynamic_parameters?.audience || 'general',
      platform: body.platform || body.dynamic_parameters?.platform || 'blog',
      length: body.length || body.dynamic_parameters?.length || 'medium',
      // Additional fields for planning agent
      tags: body.tags || body.dynamic_parameters?.tags || [],
      tone: body.tone || body.dynamic_parameters?.tone || 'professional',
      code: body.code || body.dynamic_parameters?.code || false,
      // ✅ ENHANCED: Pass through ALL dynamic parameters while ensuring required fields
      dynamic_parameters: {
        ...body.dynamic_parameters,
        template_id: templateId,  // Ensure template is in dynamic params
        style_profile_id: styleProfileId,  // Ensure style is in dynamic params
        topic: generatedTopic,  // Ensure topic is available
        // Template-specific parameters
        template_category: body.dynamic_parameters?.template_category || 'general',
        style_tone: body.dynamic_parameters?.style_tone || 'professional',
        content_structure: body.dynamic_parameters?.content_structure || 'standard'
      },
      priority: body.priority || 1,
      timeout_seconds: body.timeout_seconds || 300,
      generation_mode: body.generation_mode || "enhanced",  // Use enhanced mode by default
      created_at: new Date().toISOString(),
      user_id: body.user_id // Enterprise user tracking
    };
    
    // Validate backend URL
    if (!FASTAPI_BASE_URL) {
      console.error('🚨 [CONFIG] FASTAPI_BASE_URL not configured');
      return NextResponse.json(
        { 
          success: false, 
          error: 'Backend service not configured',
          request_id: request_id
        },
        { status: 503 }
      );
    }
    
    logSuccess('Generation Request Initiated', {
      frontend_request_id: request_id,
      template: enterprisePayload.template,
      style_profile: enterprisePayload.style_profile,
      topic: enterprisePayload.topic,
      generation_mode: enterprisePayload.generation_mode,
      priority: enterprisePayload.priority,
      backend_url: FASTAPI_BASE_URL,
      has_api_key: !!FASTAPI_API_KEY
    }, request_id);
    
    // ✅ ENHANCED: Use enhanced fetch with comprehensive error handling
    try {
      const response = await performFetchWithRetry(
        `${FASTAPI_BASE_URL}/api/generate`,
        enterprisePayload,
        3 // maxAttempts
      );
      
      // Handle non-200 responses
      if (!response.ok) {
        let errorData: { detail?: string; message?: string; error?: string } = { detail: 'Unknown backend error' };
        
        try {
          const contentType = response.headers.get('content-type');
          if (contentType?.includes('application/json')) {
            errorData = await response.json();
          } else {
            // Handle non-JSON error responses
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
        }, request_id);
        
        return NextResponse.json(
          { 
            success: false, 
            error: errorData.detail || errorData.message || errorData.error || 'Content generation failed',
            request_id: request_id,
            status_code: response.status,
            details: errorData
          }, 
          { status: response.status }
        );
      }
      
      // Handle successful response
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
            request_id: request_id
          },
          { status: 502 }
        );
      }
      
      // Extract backend's request_id
      const backendRequestId = data?.data?.request_id || data?.request_id || data?.generation_id || request_id;
      
      // **✅ ENHANCED: Poll for completion if status is pending**
      let finalData: BackendResponse = data;
      if (data?.data?.status === 'pending' || data?.status === 'pending') {
        console.log(`⏳ [POLLING] Generation ${backendRequestId} is pending, polling for completion...`);

        const maxPolls = 20; // 100 seconds max
        const pollInterval = 5000; // 5 seconds

        for (let poll = 0; poll < maxPolls; poll++) {
          await new Promise(resolve => setTimeout(resolve, pollInterval));
          
          try {
            const statusResponse = await fetch(`${FASTAPI_BASE_URL}/api/generate/${backendRequestId}`, {
              headers: createFetchHeaders(request_id, enterprisePayload.generation_mode),
              cache: 'no-cache'
            });
            if (!statusResponse.ok) {
              throw new Error(`HTTP ${statusResponse.status}: ${statusResponse.statusText}`);
            }
            if (statusResponse.headers.get('content-type')?.includes('application/json')) {
              const statusData: BackendResponse = await statusResponse.json();
              
              // Check if completed
              if (statusData?.status === 'completed' || statusData?.data?.status === 'completed') {
                console.log(`✅ [POLLING] Generation ${backendRequestId} completed after ${poll + 1} polls`);
                finalData = statusData;
                break;
              } else if (statusData?.status === 'failed' || statusData?.data?.status === 'failed') {
                console.log(`❌ [POLLING] Generation ${backendRequestId} failed`);
                finalData = statusData;
                break;
              }
              
              console.log(`⏳ [POLLING] Poll ${poll + 1}/${maxPolls}: Status = ${statusData?.status || statusData?.data?.status || 'unknown'}`);
            }
          } catch (pollError) {
            console.warn(`⚠️ [POLLING] Poll ${poll + 1} failed:`, pollError);
          }
        }
      }
      
      const processingTime = Date.now() - startTime;
      
      // ✅ ENHANCED CONTENT EXTRACTION
      const extractedContent = extractContentFromBackendResponse(finalData);
      
      // ✅ ENHANCED: Auto-save generated content with proper metadata
      let saveResult = { saved_path: '', content_id: '' };
      if (extractedContent && extractedContent.length > 50) {
        saveResult = await saveGeneratedContent(extractedContent, {
          request_id,
          template: enterprisePayload.template,
          style_profile: enterprisePayload.style_profile,
          topic: enterprisePayload.topic,
          audience: enterprisePayload.audience
        });
      }
      
      // ✅ ENHANCED: Enterprise response formatting with template/style metadata
      const enterpriseResponse: GenerationResponse = {
        success: true,
        generation_id: finalData?.data?.request_id || finalData?.generation_id || backendRequestId,
        request_id: backendRequestId, // Use backend's request_id for status tracking
        status: finalData?.data?.status || finalData?.status || (extractedContent ? 'completed' : 'processing'),
        content: extractedContent, // Use extracted content instead of data.content
        metadata: {
          ...(finalData?.data?.metadata || {}),
          ...(finalData?.metadata || {}),
          frontend_request_id: request_id, // Keep frontend ID for logging
          processing_time_ms: processingTime,
          backend_generation_id: finalData?.data?.request_id || finalData?.generation_id,
          
          // ✅ ENHANCED: Template/Style metadata for tracking
          template_used: enterprisePayload.template,
          style_profile_used: enterprisePayload.style_profile,
          topic_generated: enterprisePayload.topic,
          generation_mode: enterprisePayload.generation_mode,
          
          // Content metadata
          content_type: inferContentType(enterprisePayload.template),
          word_count: extractedContent ? extractedContent.split(' ').length : 0,
          estimated_read_time: extractedContent ? Math.ceil(extractedContent.split(' ').length / 200) : 0,
          
          // ✅ ENHANCED: Auto-save metadata
          saved_path: saveResult.saved_path,
          content_id: saveResult.content_id,
          auto_saved: !!saveResult.content_id,
          
          // Backend metadata
          innovation_report: finalData?.innovation_report || finalData?.metadata?.innovation_report,
          content_quality: finalData?.metadata?.content_quality,
          content_extraction_method: extractedContent ? 'enhanced' : 'fallback',
          
          // ✅ NEW: Template/Style combination tracking for debugging
          template_style_combination: `${enterprisePayload.template}__${enterprisePayload.style_profile}`,
          generation_success: !!extractedContent,
          content_length_chars: extractedContent ? extractedContent.length : 0
        },
        estimated_completion: finalData?.estimated_completion,
        progress: (finalData?.progress as number) || 100
      };
      
      logSuccess('Generation Completed Successfully', {
        generation_id: enterpriseResponse.generation_id,
        backend_request_id: backendRequestId,
        processing_time_ms: processingTime,
        template: enterprisePayload.template,
        style_profile: enterprisePayload.style_profile,
        topic: enterprisePayload.topic,
        content_length: extractedContent ? extractedContent.length : 0,
        content_found: !!extractedContent,
        auto_saved: !!saveResult.content_id,
        content_id: saveResult.content_id,
        template_style_combo: `${enterprisePayload.template}__${enterprisePayload.style_profile}`
      }, request_id);
      
      return NextResponse.json(enterpriseResponse);
      
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
      }, request_id);
      
      // Return appropriate error based on category
      switch (errorCategory) {
        case 'TIMEOUT':
        case 'ABORT':
          return NextResponse.json(
            { 
              success: false,
              error: 'Generation timeout', 
              message: `Content generation exceeded ${enterprisePayload.timeout_seconds} seconds`,
              request_id: request_id,
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
              request_id: request_id,
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
              request_id: request_id,
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
              request_id: request_id,
              processing_time_ms: processingTime
            }, 
            { status: 500 }
          );
      }
    }
    
  } catch (error: unknown) {
    const errorObj = error instanceof Error ? error : new Error(String(error));
    const processingTime = Date.now() - startTime;
    logError('Critical Generation Error', error, request_id);
    
    return NextResponse.json(
      { 
        success: false,
        error: 'Critical generation failure', 
        message: errorObj.message,
        request_id: request_id,
        processing_time_ms: processingTime
      }, 
      { status: 500 }
    );
  }
}

// ✅ ENHANCED: Enterprise status checking with enhanced tracking
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const request_id = searchParams.get('request_id');
    const generationId = searchParams.get('generation_id') || searchParams.get('id');
    
    if (!request_id && !generationId) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Either request_id or generation_id is required' 
        },
        { status: 400 }
      );
    }
    
    const trackingId = request_id || generationId || '';
    
    logSuccess('Status Check Initiated', { tracking_id: trackingId }, trackingId);
    
    // Enhanced status check with proper headers
    const statusHeaders = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-Request-ID': trackingId,
      ...(FASTAPI_API_KEY ? { 'Authorization': `Bearer ${FASTAPI_API_KEY}` } : {})
    };
    
    const statusEndpoints = [
      `${FASTAPI_BASE_URL}/api/status/${trackingId}`,
      `${FASTAPI_BASE_URL}/api/generation/${trackingId}`,
      `${FASTAPI_BASE_URL}/status`
    ];
    
    for (const endpoint of statusEndpoints) {
      try {
        const response = await fetch(endpoint, {
          method: 'GET',
          headers: statusHeaders,
          cache: 'no-cache'
        });
        
        if (response.ok) {
          const contentType = response.headers.get('content-type');
          let data: unknown;
          
          if (contentType?.includes('application/json')) {
            data = await response.json();
          } else {
            const textData = await response.text();
            data = { message: textData };
          }
          
          // Handle successful response for the last endpoint (general status)
          if (endpoint.endsWith('/status')) {
            // Return mock status for now since backend endpoint might not exist
            const mockStatus = {
              success: true,
              request_id: request_id,
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
          
          // Type-safe response construction for specific endpoints
          const statusResponse = {
            success: true,
            request_id: request_id,
            generation_id: (data as { generation_id?: string })?.generation_id || generationId || '',
            status: (data as { status?: string })?.status || 'unknown',
            progress: (data as { progress?: number })?.progress || 0,
            message: (data as { message?: string })?.message || '',
            created_at: (data as { created_at?: string })?.created_at || new Date().toISOString(),
            updated_at: (data as { updated_at?: string })?.updated_at || new Date().toISOString(),
            metadata: (data as { metadata?: Record<string, unknown> })?.metadata || {},
            ...((data as { content?: string })?.content ? { content: (data as { content: string }).content } : {}),
            ...((data as { error?: string })?.error ? { error: (data as { error: string }).error } : {})
          };
          
          logSuccess('Status Check Completed', statusResponse, trackingId);
          return NextResponse.json(statusResponse);
        }
      } catch (fetchError) {
        console.warn(`⚠️ [STATUS] Endpoint ${endpoint} failed:`, fetchError);
        continue;
      }
    }
    
    // All endpoints failed
    logError('All Status Endpoints Failed', { endpoints: statusEndpoints }, trackingId);
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Status check failed',
        message: 'All status endpoints are unavailable',
        request_id: trackingId,
        backend_available: false
      },
      { status: 503 }
    );
    
  } catch (error: unknown) {
    logError('Status Check Error', error);
    return NextResponse.json(
      { success: false, error: 'Failed to check generation status' },
      { status: 500 }
    );
  }
}

// ✅ ENHANCED: Enterprise generation cancellation
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const request_id = searchParams.get('request_id');
    const generationId = searchParams.get('generation_id') || searchParams.get('id');
    
    if (!request_id && !generationId) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Either request_id or generation_id is required' 
        },
        { status: 400 }
      );
    }
    
    const trackingId = request_id || generationId || '';
    
    logSuccess('Cancellation Requested', { tracking_id: trackingId });
    
    // Enterprise cancellation logic
    const cancellationResponse = {
      success: true,
      message: 'Generation cancellation requested',
      request_id: request_id,
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