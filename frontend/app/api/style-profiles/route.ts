// frontend/app/api/style-profiles/route.ts
import { NextRequest, NextResponse } from 'next/server';
import type { APIResponse, BackendStyleProfile, PaginatedResponse } from '@/types/api';

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const page = url.searchParams.get('page') || '1';
    const limit = url.searchParams.get('limit') || '100';
    const search = url.searchParams.get('search') || '';
    const category = url.searchParams.get('category') || '';

    console.log('📤 Fetching style profiles from FastAPI backend:', {
      page, limit, search, category
    });

    // Build query parameters for backend
    const backendParams = new URLSearchParams({
      page,
      limit,
      search,
      category
    });

    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/style-profiles?${backendParams}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
      // Add cache control
      next: { revalidate: 300 } // Cache for 5 minutes
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ FastAPI backend error:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      });
      
      // Fallback to local file loading
      try {
        console.log('🔄 Falling back to local style profile loading');
        const { readYamlFromDir } = await import('@/lib/file-loader');

        interface LocalStyleProfile {
          name: string;
          description: string;
          category?: string;
          [key: string]: unknown;
        }

        const pageNum = parseInt(page, 10);
        const limitNum = parseInt(limit, 10);
        const searchLower = search.toLowerCase();
        const categoryLower = category.toLowerCase();

        // Load all style profiles from local files
        let profiles = await readYamlFromDir<LocalStyleProfile>('style-profiles');

        // DEDUPLICATE BY NAME - this fixes the duplicate key error
        const uniqueProfiles = profiles.filter((profile, index, arr) => 
          arr.findIndex(p => p.name === profile.name) === index
        );

        console.log(`🔍 Loaded ${profiles.length} profiles, deduplicated to ${uniqueProfiles.length}`);
        profiles = uniqueProfiles;

        // Apply search filter
        if (search) {
          profiles = profiles.filter(
            (profile) =>
              profile.name.toLowerCase().includes(searchLower) ||
              profile.description.toLowerCase().includes(searchLower)
          );
        }

        // Apply category filter
        if (category) {
          profiles = profiles.filter(
            (profile) => profile.category?.toLowerCase() === categoryLower
          );
        }

        // Pagination
        const total = profiles.length;
        const totalPages = Math.ceil(total / limitNum);
        const startIndex = (pageNum - 1) * limitNum;
        const paginated = profiles.slice(startIndex, startIndex + limitNum);

        return NextResponse.json({
          success: true,
          data: {
            items: paginated,
            pagination: {
              page: pageNum,
              limit: limitNum,
              total,
              totalPages,
              hasNext: pageNum < totalPages,
              hasPrev: pageNum > 1,
            },
          },
          fallback: true
        });
      } catch (fallbackError) {
        console.error('❌ Fallback also failed:', fallbackError);
        return NextResponse.json({
          success: false,
          error: {
            code: 'STYLE_PROFILE_LOAD_FAILED',
            message: 'Could not load style profiles from backend or local files',
            details: errorText,
          },
        }, { status: 500 });
      }
    }

    const data = await response.json();
    console.log('✅ Style profiles loaded from FastAPI:', {
      count: data.data?.items?.length || 0,
      total: data.data?.pagination?.total || 0,
      success: data.success
    });

    // Transform and deduplicate backend response too
    const items = data.data?.items || [];
    const uniqueItems = items.filter((profile: BackendStyleProfile, index: number, arr: BackendStyleProfile[]) => 
      arr.findIndex(p => p.name === profile.name) === index
    );

    console.log(`🔍 Backend returned ${items.length} profiles, deduplicated to ${uniqueItems.length}`);

    // Transform backend response to match your frontend's expected format
    const transformedResponse: APIResponse<PaginatedResponse<BackendStyleProfile>> = {
      success: data.success,
      data: {
        items: uniqueItems.map((profile: BackendStyleProfile) => ({
          id: profile.id,
          name: profile.name,
          description: profile.description,
          category: profile.category,
          tone: profile.tone,
          voice: profile.voice,
          structure: profile.structure,
          system_prompt: profile.system_prompt,
          settings: profile.settings,
          filename: profile.filename
        })),
        pagination: data.data?.pagination
          ? { ...data.data.pagination, total: uniqueItems.length }
          : {
              page: 1,
              limit: 100,
              total: uniqueItems.length,
              totalPages: Math.ceil(uniqueItems.length / parseInt(limit, 10)),
              hasNext: false,
              hasPrev: false
            }
      }
    };

    return NextResponse.json(transformedResponse);

  } catch (error) {
    console.error('🚨 Style profiles API error:', error);
    
    return NextResponse.json({
      success: false,
      error: {
        code: 'STYLE_PROFILE_PROXY_FAILED',
        message: 'Failed to fetch style profiles',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
    }, { status: 500 });
  }
}