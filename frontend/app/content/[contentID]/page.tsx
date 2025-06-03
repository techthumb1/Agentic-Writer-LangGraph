// frontend/app/content/[contentID]/page.tsx

"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

export default function ContentPage() {
  const { contentID } = useParams();
  const [content, setContent] = useState<string>("Loading...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchContent() {
      try {
        const res = await fetch(`/api/content/${contentID}`);
        if (!res.ok) throw new Error("Failed to load content");
        const data = await res.json();
        setContent(data.content);
      } catch (err: unknown) {
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError("An unknown error occurred");
        }
      }
    }

    fetchContent();
  }, [contentID]);

  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="prose mx-auto max-w-3xl py-10">
      <h1 className="text-2xl font-bold mb-4">Preview: {contentID}</h1>
      <pre className="whitespace-pre-wrap text-sm">{content}</pre>
    </div>
  );
}
