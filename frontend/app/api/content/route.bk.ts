// frontend/app/api/content/route.ts
import { NextRequest, NextResponse } from 'next/server';
import fs from "fs/promises";
import path from "path";

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;
if (!FASTAPI_BASE_URL || !FASTAPI_API_KEY) {
  throw new Error('FASTAPI_BASE_URL and FASTAPI_API_KEY must be set in environment variables');
}

// Enterprise interfaces
interface ContentSummary {
  id: string;
  title: string;
  template: string;
  style_profile?: string;
  status: 'draft' | 'published' | 'archived' | 'generating';
  created_at: string;
  updated_at: string;
  content_preview: string;
  word_count?: number;
  generated_by: string;
  version: number;
}

interface ContentListResponse {
  success: boolean;
  content: ContentSummary[];
  total: number;
  pagination?: {
    page: number;
    limit: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  source: 'backend' | 'local_storage' | 'hybrid';
  error?: string;
}

interface CreateContentRequest {
  title: string;
  template: string;
  style_profile?: string;
  content?: string;
  dynamic_parameters?: Record<string, unknown>;
  priority?: number;
  generation_mode?: string;
}

// Enterprise logging
const logContentOperation = (operation: string, success: boolean, details?: unknown) => {
  const logData = {
    timestamp: new Date().toISOString(),
    operation,
    success,
    ...(typeof details === 'object' && details !== null ? { details } : {})
  };
  console.log(`📋 [CONTENT-LIST] ${operation}:`, JSON.stringify(logData, null, 2));
};

// Fetch content list from backend
async function fetchContentFromBackend(page = 1, limit = 50, search = '', status = ''): Promise<ContentListResponse | null> {
  try {
    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(search && { search }),
      ...(status && { status })
    });

    const response = await fetch(`${FASTAPI_BASE_URL}/api/content?${queryParams}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) {
      if (response.status === 404) {
        return null; // Backend doesn't have content endpoint yet
      }
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    logContentOperation('fetch_backend', true, { count: data.content?.length || 0 });
    
    return {
      success: true,
      content: data.content || [],
      total: data.total || 0,
      pagination: data.pagination,
      source: 'backend'
    };

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Backend fetch failed';
    logContentOperation('fetch_backend', false, { error: errorMsg });
    return null;
  }
}

// Scan local storage for content (fallback/legacy)
async function scanLocalStorageContent(): Promise<ContentSummary[]> {
  try {
    const baseDir = path.join(process.cwd(), "../storage");
    const content: ContentSummary[] = [];
    
    try {
      await fs.access(baseDir);
    } catch {
      return []; // No storage directory
    }

    const directories = await fs.readdir(baseDir);
    
    for (const directory of directories) {
      const dirPath = path.join(baseDir, directory);
      
      const stat = await fs.stat(dirPath).catch(() => null);
      if (!stat?.isDirectory()) continue;
      
      // Look for content files in each directory
      const files = await fs.readdir(dirPath).catch(() => []);
      
      for (const fileName of files) {
        if (fileName.endsWith('.json') || fileName.endsWith('.md')) {
          const filePath = path.join(dirPath, fileName);
          
          try {
            const fileContent = await fs.readFile(filePath, "utf-8");
            let parsedContent;
            
            if (fileName.endsWith('.json')) {
              parsedContent = JSON.parse(fileContent);
            } else {
              // Handle markdown
              const contentId = fileName.replace('.md', '');
              parsedContent = {
                id: contentId,
                title: `Content ${contentId}`,
                body: fileContent.substring(0, 200) + '...'
              };
            }
            
            const contentId = parsedContent.id || fileName.replace(/\.(json|md)$/, '');
            
            content.push({
              id: contentId,
              title: parsedContent.title || `Content ${contentId}`,
              template: parsedContent.template_used || parsedContent.template || directory,
              style_profile: parsedContent.style_profile_used || parsedContent.style_profile,
              status: parsedContent.status || 'draft',
              created_at: parsedContent.created_at || new Date().toISOString(),
              updated_at: parsedContent.updated_at || new Date().toISOString(),
              content_preview: (parsedContent.body || parsedContent.content || fileContent).substring(0, 150) + '...',
              word_count: parsedContent.word_count,
              generated_by: parsedContent.generated_by || 'legacy_system',
              version: parsedContent.version || 1
            });
            
          } catch {
            // Skip problematic files
            continue;
          }
        }
      }
    }
    
    logContentOperation('scan_local_storage', true, { count: content.length });
    return content;
    
  } catch (error) {
    logContentOperation('scan_local_storage', false, { error: error instanceof Error ? error.message : 'Unknown error' });
    return [];
  }
}

// GET endpoint - List all content
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1', 10);
    const limit = parseInt(searchParams.get('limit') || '50', 10);
    const search = searchParams.get('search') || '';
    const status = searchParams.get('status') || '';
    
    logContentOperation('list_request', true, { page, limit, search, status });
    
    // Enterprise strategy: Try backend first, then augment with local storage
    const backendResult = await fetchContentFromBackend(page, limit, search, status);
    
    if (backendResult) {
      // Backend available - use backend data
      return NextResponse.json(backendResult);
    }
    
    // Fallback to local storage scan
    const localContent = await scanLocalStorageContent();
    
    // Apply filters to local content
    let filteredContent = localContent;
    
    if (search) {
      filteredContent = localContent.filter(item => 
        item.title.toLowerCase().includes(search.toLowerCase()) ||
        item.content_preview.toLowerCase().includes(search.toLowerCase()) ||
        item.template.toLowerCase().includes(search.toLowerCase())
      );
    }
    
    if (status) {
      filteredContent = filteredContent.filter(item => item.status === status);
    }
    
    // Apply pagination to local content
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedContent = filteredContent.slice(startIndex, endIndex);
    
    const response: ContentListResponse = {
      success: true,
      content: paginatedContent,
      total: filteredContent.length,
      pagination: {
        page,
        limit,
        totalPages: Math.ceil(filteredContent.length / limit),
        hasNext: endIndex < filteredContent.length,
        hasPrev: page > 1
      },
      source: 'local_storage'
    };
    
    return NextResponse.json(response);
    
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Failed to fetch content';
    logContentOperation('list_request', false, { error: errorMsg });
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch content list',
        message: errorMsg
      },
      { status: 500 }
    );
  }
}

// POST endpoint - Create new content
export async function POST(request: NextRequest) {
  try {
    const body: CreateContentRequest = await request.json();
    
    // Enterprise validation
    if (!body.title || !body.template) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Validation failed',
          details: 'Title and template are required'
        },
        { status: 400 }
      );
    }
    
    logContentOperation('create_request', true, { 
      title: body.title, 
      template: body.template,
      style_profile: body.style_profile 
    });
    
    // Enterprise content creation payload
    const createPayload = {
      title: body.title,
      template: body.template,
      style_profile: body.style_profile || 'beginner_friendly',
      content: body.content || '',
      dynamic_parameters: body.dynamic_parameters || {},
      priority: body.priority || 1,
      generation_mode: body.generation_mode || 'standard',
      created_at: new Date().toISOString()
    };
    
    // Try to create via backend first
    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/content`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${FASTAPI_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(createPayload),
        signal: AbortSignal.timeout(30000), // 30 second timeout for creation
      });

      if (response.ok) {
        const data = await response.json();
        logContentOperation('create_backend', true, { content_id: data.id });
        
        return NextResponse.json({
          success: true,
          content: data,
          message: 'Content created successfully via backend',
          source: 'backend'
        });
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Backend creation failed' }));
        logContentOperation('create_backend', false, { error: errorData.detail });
        
        // Don't fall back for creation - return the backend error
        return NextResponse.json(
          { 
            success: false, 
            error: errorData.detail || 'Failed to create content',
            details: errorData
          },
          { status: response.status }
        );
      }
      
    } catch (backendError) {
      logContentOperation('create_backend', false, { 
        error: backendError instanceof Error ? backendError.message : 'Backend unavailable'
      });
      
      // Backend unavailable - create mock response for development
      const mockContent = {
        id: `mock_${Date.now()}`,
        title: body.title,
        template: body.template,
        style_profile: body.style_profile || 'beginner_friendly',
        status: 'draft' as const,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        content: body.content || '',
        content_preview: (body.content || 'New content created').substring(0, 150) + '...',
        word_count: body.content ? body.content.split(' ').length : 0,
        generated_by: 'frontend_mock',
        version: 1
      };
      
      return NextResponse.json({
        success: true,
        content: mockContent,
        message: 'Content created as draft (backend unavailable)',
        source: 'mock'
      });
    }
    
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Content creation failed';
    logContentOperation('create_request', false, { error: errorMsg });
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to create content',
        message: errorMsg
      },
      { status: 500 }
    );
  }
}

// PUT endpoint - Bulk operations (optional enterprise feature)
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, content_ids } = body;
    
    if (!action || !Array.isArray(content_ids)) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Invalid bulk operation request' 
        },
        { status: 400 }
      );
    }
    
    logContentOperation('bulk_operation', true, { action, count: content_ids.length });
    
    // Forward bulk operation to backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/content/bulk`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Bulk operation failed' }));
      return NextResponse.json(
        { 
          success: false, 
          error: errorData.detail || 'Bulk operation failed' 
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    return NextResponse.json({
      success: true,
      result: data,
      message: `Bulk ${action} completed successfully`
    });
    
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Bulk operation failed';
    logContentOperation('bulk_operation', false, { error: errorMsg });
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Bulk operation failed',
        message: errorMsg
      },
      { status: 500 }
    );
  }
}