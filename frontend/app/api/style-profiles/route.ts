//frontend/app/api/style_profiles/route.ts

import { NextRequest, NextResponse } from 'next/server';
import { StyleProfile, APIResponse, PaginatedResponse } from '@/types';
import { readYamlFromDir } from '@/lib/file-loader';
import { PAGINATION } from '@/lib/constants';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || PAGINATION.DEFAULT_LIMIT.toString());
    const search = searchParams.get('search') || '';
    const category = searchParams.get('category') || '';

    let profiles = await readYamlFromDir<StyleProfile>('style-profiles');

    if (search) {
      profiles = profiles.filter(profile =>
        profile.name.toLowerCase().includes(search.toLowerCase()) ||
        profile.description.toLowerCase().includes(search.toLowerCase())
      );
    }

    if (category) {
      profiles = profiles.filter(profile => profile.category === category);
    }

    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginated = profiles.slice(startIndex, endIndex);

    const response: APIResponse<PaginatedResponse<StyleProfile>> = {
      success: true,
      data: {
        items: paginated,
        pagination: {
          page,
          limit,
          total: profiles.length,
          totalPages: Math.ceil(profiles.length / limit),
          hasNext: endIndex < profiles.length,
          hasPrev: page > 1
        }
      }
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Error fetching style profiles:', error);

    return NextResponse.json({
      success: false,
      error: {
        code: 'STYLE_PROFILE_LOAD_FAILED',
        message: 'Could not load style profiles',
        details: error instanceof Error ? error.message : 'Unknown error'
      }
    }, { status: 500 });
  }
}
