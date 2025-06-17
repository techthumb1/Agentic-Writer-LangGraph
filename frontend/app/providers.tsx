// File: frontend/app/providers.tsx
// Update your existing providers.tsx file to include SessionProvider

"use client";

import { SessionProvider } from 'next-auth/react';
import { Session } from 'next-auth';
import { ReactQueryProvider } from '@/lib/react-query-provider';
import React from "react";

interface ProvidersProps {
  children: React.ReactNode;
  session?: Session | null;
}

export function Providers({ children, session }: ProvidersProps) {
  return (
    <SessionProvider session={session}>
      <ReactQueryProvider>
        {children}
      </ReactQueryProvider>
    </SessionProvider>
  );
}