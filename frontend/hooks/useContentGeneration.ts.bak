// ───────────────────────────────────────────────
// 📁 hooks/useContentGeneration.ts
// ───────────────────────────────────────────────

import { useMutation, useQuery } from '@tanstack/react-query';
import {
  ContentTemplate,
  StyleProfile,
  GeneratedContent,
  GenerateContentPayload,
} from '@/types/content';

export function useTemplates() {
  return useQuery<ContentTemplate[]>({
    queryKey: ['templates'],
    queryFn: async () => {
      const res = await fetch('/api/templates');
      if (!res.ok) throw new Error('Failed to fetch templates');
      return res.json();
    },
  });
}

export function useStyleProfiles() {
  return useQuery<StyleProfile[]>({
    queryKey: ['styleProfiles'],
    queryFn: async () => {
      const res = await fetch('/api/style-profiles');
      if (!res.ok) throw new Error('Failed to fetch style profiles');
      return res.json();
    },
  });
}

export function useGenerateContent(onSuccess: (data: GeneratedContent) => void, onError: (error: Error) => void) {
  return useMutation<GeneratedContent, Error, GenerateContentPayload>({
    mutationFn: async (payload) => {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to generate content');
      }
      const json = await res.json();
      return json.data; // only return the `data` field to match `GeneratedContent`

    },
    onSuccess,
    onError,
  });
}