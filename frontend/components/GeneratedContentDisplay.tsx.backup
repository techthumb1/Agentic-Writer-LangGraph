"use client";

import React, { useEffect } from "react";

interface GeneratedContentDisplayProps {
  generatedContent: string;
  isLoading: boolean;
}

export default function GeneratedContentDisplay({
  generatedContent,
  isLoading,
}: GeneratedContentDisplayProps) {
  useEffect(() => {
    console.log("🧾 GeneratedContentDisplay received:", {
      isLoading,
      typeofContent: typeof generatedContent,
      contentLength: generatedContent?.length,
      trimmed: generatedContent?.trim(),
    });
  }, [generatedContent, isLoading]);

  const safeTrimmed = typeof generatedContent === "string" ? generatedContent.trim() : "";

  return (
    <section className="mt-8">
      <h2 className="text-2xl font-semibold text-gray-900 mb-4">Generated Content</h2>

      <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 shadow-sm min-h-[150px] text-sm leading-relaxed">
        {isLoading ? (
          <p className="text-muted-foreground italic">Generating...</p>
        ) : safeTrimmed.length > 0 ? (
          <div
            className="prose prose-neutral max-w-none"
            dangerouslySetInnerHTML={{ __html: safeTrimmed }}
          />
        ) : (
          <p className="text-muted-foreground italic">No content yet.</p>
        )}
      </div>
    </section>
  );
}
