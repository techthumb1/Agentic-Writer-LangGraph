// frontend/hooks/useStyleProfiles.ts - FIXED VERSION
import { useQuery } from "@tanstack/react-query";

interface StyleProfile {
  id: string;
  name: string;
  description: string;
  category: string;
  platform?: string;
  tone?: string;
  voice?: string;
  structure?: string;
  audience?: string;
  system_prompt?: string;
  length_limit?: Record<string, unknown>;
  settings: Record<string, unknown>;
  formatting: Record<string, unknown>;
  metadata: Record<string, unknown>;
  filename: string;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000';

async function fetcher(url: string): Promise<StyleProfile[]> {
  console.log('🚀 Fetching style profiles from:', url);
  
  const res = await fetch(url);
  if (!res.ok) {
    const errorText = await res.text();
    console.error('❌ Style profiles fetch failed:', res.status, res.statusText, errorText);
    throw new Error(`Failed to fetch style profiles: ${res.status} ${res.statusText}`);
  }
  
  const result = await res.json();
  
  console.log('🔍 Style profiles API response structure:', {
    type: typeof result,
    isArray: Array.isArray(result),
    keys: result && typeof result === 'object' ? Object.keys(result) : 'not object',
    hasProfiles: result?.profiles !== undefined,
    hasSuccess: result?.success !== undefined,
    profilesLength: result?.profiles?.length,
    resultLength: Array.isArray(result) ? result.length : 'not array'
  });
  
  // ✅ NEW: Handle our API route format { profiles: [...], success: true }
  if (result && typeof result === 'object' && result.profiles && Array.isArray(result.profiles)) {
    console.log(`✅ Found profiles in wrapper object: ${result.profiles.length} profiles`);
    return result.profiles;
  }
  
  // Legacy: Check for paginated response structure
  if (result.success && result.data?.items && Array.isArray(result.data.items)) {
    const profiles = result.data.items.map((profile: StyleProfile) => ({
      id: profile.id,
      name: profile.name,
      description: profile.description || '',
      category: profile.category || 'general',
      platform: profile.platform,
      tone: profile.tone,
      voice: profile.voice,
      structure: profile.structure,
      audience: profile.audience,
      system_prompt: profile.system_prompt,
      length_limit: profile.length_limit || {},
      settings: profile.settings || {},
      formatting: profile.formatting || {},
      metadata: profile.metadata || {},
      filename: profile.filename
    }));
    
    console.log(`✅ Loaded ${profiles.length} real style profiles from legacy format`);
    return profiles;
  }
  
  // Fallback: Direct array
  if (Array.isArray(result)) {
    console.log(`✅ Using direct array format: ${result.length} profiles`);
    return result;
  }
  
  // Enhanced error logging
  console.error('❌ Style profiles API error - Full result:', JSON.stringify(result, null, 2));
  console.error('❌ No valid profile format found');
  
  throw new Error(result.error?.message || 'Failed to load style profiles - unexpected response format');
}

// ✅ FIXED: Return interface that matches component expectations
export function useStyleProfiles() {
  const query = useQuery<StyleProfile[], Error>({
    queryKey: ['style-profiles'],
    queryFn: async () => {
      console.log('🔄 useStyleProfiles: Starting fetch...');
      const result = await fetcher(`${BACKEND_URL}/api/style-profiles?page=1&limit=100`);
      
      console.log('🔍 useStyleProfiles: Final result:', {
        type: typeof result,
        isArray: Array.isArray(result),
        length: Array.isArray(result) ? result.length : 'not array',
        firstItem: Array.isArray(result) && result.length > 0 ? result[0].id : 'none'
      });
      
      return result;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  // ✅ FIXED: Return both interfaces to support all components
  return {
    // Standard React Query interface (for page.tsx)
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    
    // Component-expected interface (for StyleProfilesSelector.tsx)
    styleProfiles: query.data,
  };
}

export function useStyleProfile(id: string) {
  const { data: profiles, isLoading, error } = useStyleProfiles();
  
  const profile = Array.isArray(profiles) ? profiles.find(p => p.id === id) : undefined;
  
  return {
    data: profile,
    isLoading,
    error: profile ? null : error
  };
}

export type { StyleProfile };