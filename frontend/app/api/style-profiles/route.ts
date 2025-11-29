// app/api/style-profiles/route.ts
import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_BASE_URL = process.env.FASTAPI_BASE_URL;
const FASTAPI_API_KEY = process.env.FASTAPI_API_KEY;

console.log('🔑 [STYLE-PROFILES] Environment check:', {
  hasBaseUrl: !!FASTAPI_BASE_URL,
  hasApiKey: !!FASTAPI_API_KEY,
  baseUrl: FASTAPI_BASE_URL,
  keyPreview: FASTAPI_API_KEY ? `${FASTAPI_API_KEY.substring(0, 10)}...` : 'MISSING'
});

interface BackendStyleProfile {
  id: string;
  name: string;
  description: string;
  category?: string;
  tone?: string;
  voice?: string;
  structure?: string;
  system_prompt?: string;
  settings?: Record<string, unknown>;
  filename?: string;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = searchParams.get('page') || '1';
    const limit = searchParams.get('limit') || '100';
    const search = searchParams.get('search') || '';
    const category = searchParams.get('category') || '';

    console.log(`🔍 [STYLE-PROFILES] Fetching profiles - page: ${page}, limit: ${limit}, search: "${search}", category: "${category}"`);

    // Build query parameters for backend
    const params = new URLSearchParams({
      page,
      limit,
      ...(search && { search }),
      ...(category && { category }),
    });

    console.log('🔍 [STYLE-PROFILES] Making request to:', `${FASTAPI_BASE_URL}/api/style-profiles?${params}`);

    const response = await fetch(`${FASTAPI_BASE_URL}/api/style-profiles?${params}`, {
      method: 'GET',
      headers: {
        ...(FASTAPI_API_KEY && { 'Authorization': `Bearer ${FASTAPI_API_KEY}` }),
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      signal: AbortSignal.timeout(10000), // 10 second timeout
    });

    if (!response.ok) {
      console.error(`❌ [STYLE-PROFILES] Backend error: ${response.status} ${response.statusText}`);
      const errorText = await response.text();
      console.error(`❌ [STYLE-PROFILES] Error details:`, errorText);
      throw new Error(`Backend responded with ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    console.log('🔍 [STYLE-PROFILES] Raw backend response type:', typeof data);
    console.log('🔍 [STYLE-PROFILES] Is array:', Array.isArray(data));
    console.log('🔍 [STYLE-PROFILES] Response keys:', data && typeof data === 'object' ? Object.keys(data) : 'primitive type');

    // ✅ FIX: Backend returns style profiles directly as an array
    let profiles: BackendStyleProfile[] = [];
    
    if (Array.isArray(data)) {
      // Backend returns profiles directly as an array
      profiles = data;
      console.log('✅ [STYLE-PROFILES] Using direct array response');
    } else if (data.data?.items) {
      profiles = data.data.items;
      console.log('✅ [STYLE-PROFILES] Using data.data.items');
    } else if (data.items) {
      profiles = data.items;
      console.log('✅ [STYLE-PROFILES] Using data.items');
    } else if (data.profiles || data.style_profiles) {
      profiles = data.profiles || data.style_profiles;
      console.log('✅ [STYLE-PROFILES] Using data.profiles/style_profiles');
    } else {
      console.warn(`⚠️ [STYLE-PROFILES] Unexpected response structure:`, Object.keys(data || {}));
      profiles = [];
    }

    console.log(`📊 [STYLE-PROFILES] Extracted ${profiles.length} profiles`);

    // Transform backend profiles to frontend format
    const transformedProfiles = profiles.map((profile) => {
      console.log('🔄 [STYLE-PROFILES] Transforming profile:', profile.id, profile.name);
      
      return {
        id: profile.id,
        name: profile.name || 'Untitled Profile',
        description: profile.description || `Style profile for ${profile.category || 'general'}`,
        category: profile.category || 'general',
        tone: profile.tone || null,
        voice: profile.voice || null,
        structure: profile.structure || null,
        system_prompt: profile.system_prompt || '',
        settings: profile.settings || {},
        filename: profile.filename || null,
        metadata: profile.metadata || {},
        isBuiltIn: true,
        isPublic: true,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    });

    console.log(`✅ [STYLE-PROFILES] Successfully transformed ${transformedProfiles.length} profiles`);
    console.log('🔍 [STYLE-PROFILES] First transformed profile:', transformedProfiles[0]);

    // Extract pagination info
    const total = Array.isArray(data) ? data.length : 
                 data.data?.total || data.total || profiles.length;
    const currentPage = parseInt(page);
    const pageLimit = parseInt(limit);
    const totalPages = Math.ceil(total / pageLimit);

    const response_data = {
      profiles: transformedProfiles,
      total,
      pagination: {
        page: currentPage,
        limit: pageLimit,
        total,
        totalPages,
      },
      success: true,
    };

    console.log(`🎯 [STYLE-PROFILES] Final response:`, {
      profilesCount: response_data.profiles.length,
      total: response_data.total,
      success: response_data.success
    });

    return NextResponse.json(response_data);

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    console.error('❌ [STYLE-PROFILES] API Error:', errorMessage);
    console.error('❌ [STYLE-PROFILES] Error stack:', error instanceof Error ? error.stack : 'No stack');

    // Return error response with fallback empty data
    return NextResponse.json(
      {
        error: 'Failed to fetch style profiles',
        message: errorMessage,
        profiles: [],
        total: 0,
        pagination: {
          page: 1,
          limit: parseInt(request.nextUrl.searchParams.get('limit') || '100'),
          total: 0,
          totalPages: 0,
        },
        success: false,
      },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    console.log(`📝 [STYLE-PROFILES] Creating new profile:`, body.name);

    const response = await fetch(`${FASTAPI_BASE_URL}/api/style-profiles`, {
      method: 'POST',
      headers: {
        ...(FASTAPI_API_KEY && { 'Authorization': `Bearer ${FASTAPI_API_KEY}` }),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`❌ [STYLE-PROFILES] Create error:`, errorText);
      throw new Error(`Backend responded with ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`✅ [STYLE-PROFILES] Profile created successfully:`, data.id);

    return NextResponse.json({
      success: true,
      profile: data,
    });

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    console.error('❌ [STYLE-PROFILES] Create Error:', errorMessage);

    return NextResponse.json(
      {
        error: 'Failed to create style profile',
        message: errorMessage,
        success: false,
      },
      { status: 500 }
    );
  }
}