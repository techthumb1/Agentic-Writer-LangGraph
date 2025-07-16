// frontend/lib/react-query-provider.tsx (Fixed TypeScript errors)
"use client";

import { QueryClient, QueryClientProvider, MutationCache, QueryCache } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';
import { toast } from '@/hooks/use-toast';

// Define proper error types
interface ApiError extends Error {
  status?: number;
  data?: unknown;
}

// Define mutation context type


// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function ReactQueryProvider({ children }: { children: any }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // With SSR, we usually want to set some default staleTime
            staleTime: 60 * 1000, // 1 minute
            gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
            retry: (failureCount, error: unknown) => {
              const apiError = error as ApiError;
              // Don't retry on 4xx errors except 408, 429
              if (
                typeof apiError?.status === 'number' &&
                apiError.status >= 400 &&
                apiError.status < 500 &&
                ![408, 429].includes(apiError.status)
              ) {
                return false;
              }
              // Retry up to 3 times for other errors
              return failureCount < 3;
            },
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
            refetchOnWindowFocus: true,
            refetchOnReconnect: true,
          },
          mutations: {
            retry: (failureCount, error: unknown) => {
              const apiError = error as ApiError;
              // Don't retry mutations on client errors
              if (typeof apiError?.status === 'number' && apiError.status >= 400 && apiError.status < 500) {
                return false;
              }
              return failureCount < 2;
            },
          },
        },
        queryCache: new QueryCache({
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          onError: (error: Error, _query) => {
            // Global error handling for queries
            const apiError = error as ApiError;
            // console statement removed
            
            // Show toast for specific errors
            if (apiError?.status === 401) {
              toast({
                title: "Authentication Error",
                description: "Please sign in to continue.",
                variant: "destructive",
              });
            } else if (apiError?.status === 403) {
              toast({
                title: "Access Denied",
                description: "You don't have permission to access this resource.",
                variant: "destructive",
              });
            } else if (apiError?.status && apiError.status >= 500) {
              toast({
                title: "Server Error",
                description: "Something went wrong on our end. Please try again later.",
                variant: "destructive",
              });
            } else if (error?.message && !apiError?.status) {
              // Network or other errors
              toast({
                title: "Connection Error",
                description: "Please check your internet connection and try again.",
                variant: "destructive",
              });
            }
          },
        }),
        mutationCache: new MutationCache({
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          onError: (error: Error, _variables: unknown) => {
            // Global error handling for mutations
            const apiError = error as ApiError;
            // console statement removed
            
            // Show toast for mutation errors
            if (apiError?.status === 422) {
              toast({
                title: "Validation Error",
                description: apiError?.message || "Please check your input and try again.",
                variant: "destructive",
              });
            } else if (apiError?.status === 409) {
              toast({
                title: "Conflict Error",
                description: "This action conflicts with existing data.",
                variant: "destructive",
              });
            }
          },
          onSuccess: (
            data: unknown,
            variables: unknown,
            context: unknown,
            mutation
          ) => {
            // Global success handling for mutations
            // mutation.options?.mutationKey is readonly, so we can safely read from it
            const mutationKey = (mutation?.options?.mutationKey?.[0] ?? '') as string;
            
            // Show success toasts for specific mutations
            if (mutationKey === 'createContent') {
              toast({
                title: "Content Created",
                description: "Your content has been successfully generated.",
                variant: "default",
              });
            } else if (mutationKey === 'updateContent') {
              toast({
                title: "Content Updated",
                description: "Your changes have been saved.",
                variant: "default",
              });
            } else if (mutationKey === 'deleteContent') {
              toast({
                title: "Content Deleted",
                description: "The content has been removed.",
                variant: "default",
              });
            }
          },
        }),
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools 
          initialIsOpen={false} 
          buttonPosition="bottom-left"
          position="bottom"
        />
      )}
    </QueryClientProvider>
  );
}