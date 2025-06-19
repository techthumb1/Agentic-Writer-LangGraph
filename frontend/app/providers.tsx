// frontend/app/providers.tsx (Complete version with all features)
"use client";

import { SessionProvider } from 'next-auth/react';
import { Session } from 'next-auth';
import { ReactQueryProvider } from '@/lib/react-query-provider';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import React from "react";

interface ProvidersProps {
  children: React.ReactNode;
  session?: Session | null;
}

export function Providers({ children, session }: ProvidersProps) {
  return (
    <SessionProvider 
      session={session} 
      basePath="/api/auth"
      refetchInterval={5 * 60} // Refetch session every 5 minutes
      refetchOnWindowFocus={true}
    >
      <ReactQueryProvider>
        <TooltipProvider delayDuration={300}>
          {children}
          {/* Toast notifications */}
          <Toaster />
        </TooltipProvider>
      </ReactQueryProvider>
    </SessionProvider>
  );
}