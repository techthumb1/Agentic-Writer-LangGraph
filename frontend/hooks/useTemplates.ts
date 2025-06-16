// frontend/hooks/useTemplates.ts
import { useQuery } from "@tanstack/react-query";

async function fetcher(url: string) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch templates");
  return res.json();
}

export function useTemplates() {
  const { data, error, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: () => fetcher("/api/templates"),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return {
    templates: data || [],
    isLoading,
    isError: !!error,
  };
}