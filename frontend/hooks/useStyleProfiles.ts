// frontend/hooks/useStyleProfiles.ts
import useSWR from "swr";

export function useStyleProfiles({ page = 1, search = "", category = "" } = {}) {
  const params = new URLSearchParams({ page: page.toString(), search, category });
  const { data, error, isLoading } = useSWR(`/api/style-profiles?${params}`, fetcher);

  return {
    profiles: data?.data?.items || [],
    pagination: data?.data?.pagination,
    isLoading,
    isError: !!error,
  };
}

async function fetcher(url: string) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch style profiles");
  return res.json();
}
