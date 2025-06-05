import { useQuery } from '@tanstack/react-query';
import { API_ENDPOINTS } from '../lib/constants';
import { APIResponse } from '../types';

export function useGenerationStatus(contentId: string) {
  return useQuery({
    queryKey: ['generation-status', contentId],
    queryFn: async (): Promise<APIResponse<{ status: string; progress: number }>> => {
      const res = await fetch(`${API_ENDPOINTS.GENERATE_CONTENT}/status?id=${contentId}`);
      if (!res.ok) throw new Error('Failed to fetch generation status');
      return res.json();
    },
    enabled: !!contentId,
    refetchInterval: 2000
  });
}
