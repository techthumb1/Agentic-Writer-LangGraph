// components/GeneratedContentDisplay.tsx
"use client";

import React from "react";

type Props = {
  generatedContent: string;
  isLoading: boolean;
};

export default function GeneratedContentDisplay({ generatedContent, isLoading }: Props) {
  return (
    <div className="mt-6">
      <h2 className="text-xl font-semibold mb-2">Generated Content</h2>
      <div className="border rounded-xl p-4 bg-muted text-sm whitespace-pre-wrap font-mono">
        {isLoading ? (
          <span className="italic text-muted-foreground">Generating...</span>
        ) : generatedContent ? (
          <div dangerouslySetInnerHTML={{ __html: generatedContent }} />
        ) : (
          <span className="italic text-muted-foreground">No content yet.</span>
        )}
      </div>
    </div>
  );
}
