// frontend/app/api/content/[contentID]/route.ts
import { NextRequest, NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY || 'your-api-key-here';

// Enterprise logging
const logContentAccess = (contentID: string, source: string, success: boolean, details?: string) => {
  const logData = {
    timestamp: new Date().toISOString(),
    content_id: contentID,
    source,
    success,
    ...(details && { details })
  };
  console.log(`📄 [CONTENT-ID] ${contentID}:`, JSON.stringify(logData, null, 2));
};

// Try backend first (enterprise approach)
async function fetchFromBackend(contentID: string): Promise<Record<string, unknown> | null> {
  try {
    const response = await fetch(`${FASTAPI_BASE_URL}/api/content/${contentID}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) {
      if (response.status === 404) {
        logContentAccess(contentID, 'backend', false, 'Not found in backend');
        return null;
      }
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    logContentAccess(contentID, 'backend', true, 'Found in backend');
    return data;

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Backend fetch failed';
    logContentAccess(contentID, 'backend', false, errorMsg);
    return null; // Fall back to local storage
  }
}

export async function GET(
  request: NextRequest,
  context: { params: { contentID: string } }  // ✅ Keep your original structure
) {
  try {
    const contentID = context.params.contentID;  // ✅ Keep your original variable naming
    
    if (!contentID || contentID.trim() === '') {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Content ID is required',
          content_id: contentID
        },
        { status: 400 }
      );
    }
    
    console.log(`🔍 [CONTENT-ID] Fetching content: ${contentID}`);
    
    // Enterprise strategy: Try backend first
    const backendResult = await fetchFromBackend(contentID);
    if (backendResult) {
      return NextResponse.json({
        success: true,
        ...backendResult,
        source: 'backend'
      });
    }
    
    // Fall back to your original local storage logic (enhanced)
    const baseDir = path.join(process.cwd(), "../storage");

    // Check if storage directory exists
    try {
      await fs.access(baseDir);
    } catch {
      logContentAccess(contentID, 'local_storage', false, 'Storage directory not accessible');
      return NextResponse.json(
        { 
          success: false,
          error: "Storage not accessible", 
          content_id: contentID
        }, 
        { status: 503 }
      );
    }

    const directories = await fs.readdir(baseDir);
    
    // Your original logic enhanced with better file searching
    for (const week of directories) {
      const weekPath = path.join(baseDir, week);
      
      // Skip if not a directory
      const stat = await fs.stat(weekPath).catch(() => null);
      if (!stat?.isDirectory()) continue;
      
      // Try multiple file patterns for better coverage
      const possibleFiles = [
        `${contentID}.json`,
        `${contentID}.md`,
        'artificial_intelligence_mock.json' // Legacy fallback
      ];
      
      for (const fileName of possibleFiles) {
        const filePath = path.join(weekPath, fileName);
        
        try {
          const file = await fs.readFile(filePath, "utf-8");
          const parsedFile = JSON.parse(file);
          
          // If it's a mock file, verify it matches our content ID
          if (fileName === 'artificial_intelligence_mock.json') {
            if (parsedFile.id && parsedFile.id !== contentID) {
              continue; // This mock doesn't match our ID
            }
          }
          
          logContentAccess(contentID, 'local_storage', true, `Found in ${week}/${fileName}`);
          
          return NextResponse.json({
            success: true,
            ...parsedFile,
            source: 'local_storage',
            content_id: contentID
          });
          
        } catch {
          continue; // keep searching other files/folders (your original logic)
        }
      }
    }

    // Content not found anywhere
    logContentAccess(contentID, 'all_sources', false, 'Content not found');
    return NextResponse.json(
      { 
        success: false,
        error: "File not found", 
        content_id: contentID,
        searched_sources: ['backend', 'local_storage']
      }, 
      { status: 404 }
    );
    
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Failed to read content";
    console.error("[api/content] error:", msg);
    
    return NextResponse.json(
      { 
        success: false,
        error: msg,
        content_id: context.params.contentID
      }, 
      { status: 500 }
    );
  }
}

// Enterprise content update endpoint
export async function PUT(
  request: NextRequest,
  context: { params: { contentID: string } }
) {
  try {
    const contentID = context.params.contentID;
    const body = await request.json();
    
    console.log(`📝 [CONTENT-ID] Updating content: ${contentID}`);
    
    // Forward update to backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/content/${contentID}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Update failed' }));
      logContentAccess(contentID, 'backend', false, `Update failed: ${errorData.detail}`);
      
      return NextResponse.json(
        { 
          success: false, 
          error: errorData.detail || 'Failed to update content',
          content_id: contentID
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    logContentAccess(contentID, 'backend', true, 'Content updated successfully');
    
    return NextResponse.json({
      success: true,
      content: data,
      message: 'Content updated successfully',
      content_id: contentID
    });
    
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Update failed';
    console.error('[api/content] update error:', errorMsg);
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to update content',
        message: errorMsg,
        content_id: context.params.contentID
      }, 
      { status: 500 }
    );
  }
}

// Enterprise content deletion
export async function DELETE(
  request: NextRequest,
  context: { params: { contentID: string } }
) {
  try {
    const contentID = context.params.contentID;
    
    console.log(`🗑️ [CONTENT-ID] Deleting content: ${contentID}`);
    
    // Forward deletion to backend
    const response = await fetch(`${FASTAPI_BASE_URL}/api/content/${contentID}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${FASTAPI_API_KEY}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Deletion failed' }));
      logContentAccess(contentID, 'backend', false, `Deletion failed: ${errorData.detail}`);
      
      return NextResponse.json(
        { 
          success: false, 
          error: errorData.detail || 'Failed to delete content',
          content_id: contentID
        },
        { status: response.status }
      );
    }

    logContentAccess(contentID, 'backend', true, 'Content deleted successfully');
    
    return NextResponse.json({
      success: true,
      message: 'Content deleted successfully',
      content_id: contentID
    });
    
  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : 'Deletion failed';
    console.error('[api/content] deletion error:', errorMsg);
    
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to delete content',
        message: errorMsg,
        content_id: context.params.contentID
      }, 
      { status: 500 }
    );
  }
}