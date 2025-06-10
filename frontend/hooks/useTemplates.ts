// frontend/hooks/useTemplates.ts
import useSWR from "swr";

export function useTemplates() {
  const { data, error, isLoading } = useSWR("/api/templates", fetcher);

  return {
    templates: data || [],
    isLoading,
    isError: !!error,
  };
}

async function fetcher(url: string) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch templates");
  return res.json();
}
