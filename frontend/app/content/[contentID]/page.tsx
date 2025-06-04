// frontend/app/content/[contentID]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

interface Article {
  title: string;
  contentHtml?: string;
  metadata?: Record<string, unknown>;
}

export default function ContentPage() {
  const { contentID } = useParams<{ contentID: string }>();
  const router = useRouter();

  const [data, setData]   = useState<Article | null>(null);
  const [isLoading, setL] = useState(true);
  const [error, setErr]   = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`/api/content/${contentID}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json: Article = await res.json();
        setData(json);
      } catch (err) {
        setErr(err instanceof Error ? err.message : "Unknown error");
        // optional redirect
        // router.push("/generate");
      } finally {
        setL(false);
      }
    };
    load();
  }, [contentID, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin mr-2" />
        Loading article…
      </div>
    );
  }

  if (error) {
    return <p className="text-center text-red-500 py-20">Error: {error}</p>;
  }

  if (!data) {
    return <p className="text-center text-muted-foreground py-20">Content not found.</p>;
  }

  const { title, contentHtml } = data;
  const fallback = `<pre>${JSON.stringify(data, null, 2)}</pre>`;

  return (
    <main className="max-w-3xl mx-auto py-12">
      <h1 className="text-3xl font-bold mb-6">{title ?? contentID}</h1>

      <article
        className="prose prose-neutral max-w-none"
        dangerouslySetInnerHTML={{ __html: contentHtml || fallback }}
      />
    </main>
  );
}
