// frontend/hooks/useStyleProfiles.ts
import { useQuery } from "@tanstack/react-query";

async function fetcher(url: string) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch style profiles");
  return res.json();
}

export function useStyleProfiles({ page = 1, search = "", category = "" } = {}) {
  const params = new URLSearchParams({ page: page.toString(), search, category });
  const { data, error, isLoading } = useQuery({
    queryKey: ['styleProfiles', page, search, category],
    queryFn: () => fetcher(`/api/style-profiles?${params}`),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  return {
    profiles: data?.data?.items || [],
    pagination: data?.data?.pagination,
    isLoading,
    isError: !!error,
  };
}