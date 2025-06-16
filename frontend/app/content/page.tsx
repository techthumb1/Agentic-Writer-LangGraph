// frontend/app/content/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Loader2, FileText } from 'lucide-react';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';

type ContentItem = {
  id: string;
  title: string;
  date: string;
};

export default function MyContentPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [contentList, setContentList] = useState<ContentItem[]>([]);

  useEffect(() => {
    // Simulate fetch - replace with real API call
    setTimeout(() => {
      setContentList([
        { id: 'intro-contrastive-learning', title: 'Intro to Contrastive Learning', date: '2025-06-01' },
        { id: 'federated-learning-101', title: 'Federated Learning 101', date: '2025-06-05' },
      ]);
      setIsLoading(false);
    }, 1000);
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8 text-gray-900 dark:text-white">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
          My Generated Content
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Access, review, and publish your saved AI-generated drafts.
        </p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
        </div>
      ) : contentList.length === 0 ? (
        <p className="text-center text-gray-600">You haven’t generated anything yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {contentList.map((item) => (
            <Card key={item.id}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-500" />
                  {item.title}
                </CardTitle>
                <CardDescription>Created on {item.date}</CardDescription>
              </CardHeader>
              <CardContent>
                <Badge variant="secondary" className="mb-3">Draft</Badge>
                <Link
                  href={`/content/${item.id}`}
                  className="text-sm text-blue-600 hover:underline"
                >
                  View Content →
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
