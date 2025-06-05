import { NextRequest, NextResponse } from 'next/server';
import { StyleProfile, APIResponse, PaginatedResponse } from '@/types';
import { readYamlFromDir } from '@/lib/file-loader';
import { PAGINATION } from '@/lib/constants';

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1', 10);
    const limit = parseInt(url.searchParams.get('limit') || PAGINATION.DEFAULT_LIMIT.toString(), 10);
    const search = url.searchParams.get('search')?.toLowerCase() || '';
    const category = url.searchParams.get('category')?.toLowerCase() || '';

    // Load all style profiles from the 'style-profiles/' YAML directory
    let profiles = await readYamlFromDir<StyleProfile>('style-profiles');

    // Apply search filter (name or description match)
    if (search) {
      profiles = profiles.filter(
        (profile) =>
          profile.name.toLowerCase().includes(search) ||
          profile.description.toLowerCase().includes(search)
      );
    }

    // Apply category filter if specified
    if (category) {
      profiles = profiles.filter(
        (profile) => profile.category?.toLowerCase() === category
      );
    }

    // Pagination
    const total = profiles.length;
    const totalPages = Math.ceil(total / limit);
    const startIndex = (page - 1) * limit;
    const paginated = profiles.slice(startIndex, startIndex + limit);

    const response: APIResponse<PaginatedResponse<StyleProfile>> = {
      success: true,
      data: {
        items: paginated,
        pagination: {
          page,
          limit,
          total,
          totalPages,
          hasNext: page < totalPages,
          hasPrev: page > 1,
        },
      },
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('❌ STYLE_PROFILE_LOAD_FAILED:', error);

    return NextResponse.json(
      {
        success: false,
        error: {
          code: 'STYLE_PROFILE_LOAD_FAILED',
          message: 'Could not load style profiles',
          details: error instanceof Error ? error.message : 'Unknown error',
        },
      },
      { status: 500 }
    );
  }
}
