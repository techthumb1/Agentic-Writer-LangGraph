"use client";

import { useEffect, useState } from "react";
//import { useSearchParams } from "next/navigation";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

interface PageProps {
  params: { id: string };
}

interface GeneratedContent {
  title: string;
  contentHtml: string;
  metadata?: Record<string, unknown>;
}

export default function ContentPage({ params }: PageProps) {
  const [content, setContent] = useState<GeneratedContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`/generated_content/${params.id}.json`);
        const json = await res.json();
        setContent(json);
      } catch (err) {
        console.error("Failed to load content:", err);
        router.push("/generate");
      } finally {
        setIsLoading(false);
      }
    };

    load();
  }, [params.id, router]);

  return (
    <div className="max-w-3xl mx-auto py-12">
      {isLoading ? (
        <div className="flex items-center justify-center space-x-2 text-sm text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading content...</span>
        </div>
      ) : content ? (
        <article>
          <h1 className="text-3xl font-bold mb-6">{content.title}</h1>
          <div
            className="prose prose-neutral max-w-none"
            dangerouslySetInnerHTML={{ __html: content.contentHtml }}
          />
        </article>
      ) : (
        <p className="text-muted-foreground italic">Content not found.</p>
      )}
    </div>
  );
}
