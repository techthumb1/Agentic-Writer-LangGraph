// frontend/hooks/useStyleProfiles.ts
import { useQuery } from "@tanstack/react-query";

interface StyleProfile {
  id: string;
  name: string;
  description: string;
  category: string;
  tone: string;
  voice: string;
  structure: string;
  system_prompt: string;
  settings: Record<string, unknown>;
  filename: string;
}

interface StyleProfilesResponse {
  style_profiles: StyleProfile[];
  total: number;
  error?: string;
}

async function fetcher(url: string): Promise<StyleProfile[]> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch style profiles: ${res.status} ${res.statusText}`);
  }
  
  const result: StyleProfilesResponse = await res.json();
  
  // Debug logging
  console.log('Style profiles API response:', result);
  
  // Check if response has style_profiles array (from our transformed API route)
  if (result.style_profiles && Array.isArray(result.style_profiles)) {
    console.log(`✅ Loaded ${result.style_profiles.length} style profiles`);
    return result.style_profiles;
  }
  
  // Handle error cases
  console.error('Style profiles API error:', result.error || 'Unexpected response format');
  throw new Error(result.error || 'Failed to load style profiles');
}

export function useStyleProfiles() {
  const { data, error, isLoading } = useQuery({
    queryKey: ['style-profiles'],
    queryFn: () => fetcher("/api/style-profiles"),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
  });

  return {
    styleProfiles: data || [],
    isLoading,
    isError: !!error,
    error: error as Error | null,
  };
}

export type { StyleProfile, StyleProfilesResponse };