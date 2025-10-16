//// frontend/app/providers.tsx (Complete version with all features)
//"use client";
//
//import { SessionProvider } from 'next-auth/react';
//import { Session } from 'next-auth';
//import { ReactQueryProvider } from '@/lib/react-query-provider';
//import { Toaster } from '@/components/ui/toaster';
//import { TooltipProvider } from '@/components/ui/tooltip';
//import React from "react";
//
//interface ProvidersProps {
//  children: React.ReactNode;
//  session?: Session | null;
//}
//
//export function Providers({ children, session }: ProvidersProps) {
//  return (
//    <SessionProvider 
//      session={session} 
//      basePath="/api/auth"
//      refetchInterval={5 * 60} // Refetch session every 5 minutes
//      refetchOnWindowFocus={true}
//    >
//      <ReactQueryProvider>
//        <TooltipProvider delayDuration={300}>
//          {children}
//          {/* Toast notifications */}
//          <Toaster />
//        </TooltipProvider>
//      </ReactQueryProvider>
//    </SessionProvider>
//  );
//}

// File: frontend/app/providers.tsx
// Client-side providers for session and other contexts

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