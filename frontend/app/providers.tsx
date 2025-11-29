//// frontend/app/providers.tsx (Complete version with all features)
'use client';

import { SessionProvider } from 'next-auth/react';
import type { Session } from 'next-auth';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

interface ProvidersProps {
  children: React.ReactNode;
  session: Session | null;
}

export function Providers({ children, session }: ProvidersProps) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        refetchOnWindowFocus: false,
      },
    },
  }));

  return (
    <SessionProvider session={session}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </SessionProvider>
  );
}