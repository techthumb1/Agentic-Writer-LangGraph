// frontend/app/auth/error/error-content.tsx
'use client';

import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, ArrowLeft, RefreshCw } from 'lucide-react';

const errors = {
  Configuration: 'There is a problem with the server configuration.',
  AccessDenied: 'You do not have permission to sign in.',
  Verification: 'The verification token has expired or has already been used.',
  Default: 'An unexpected error occurred.',
};

export function AuthErrorContent() {
  const searchParams = useSearchParams();
  const error = searchParams.get('error') as keyof typeof errors;

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-blue-900 dark:to-purple-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md border-0 shadow-xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg">
        <CardHeader className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="p-3 rounded-full bg-red-100 dark:bg-red-900/20">
              <AlertTriangle className="h-8 w-8 text-red-600 dark:text-red-400" />
            </div>
          </div>
          <div>
            <CardTitle className="text-2xl text-red-600 dark:text-red-400">
              Authentication Error
            </CardTitle>
            <CardDescription className="mt-2">
              {errors[error] || errors.Default}
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center space-y-3">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {error === 'AccessDenied' && 
                'Your account may not have the necessary permissions, or the sign-in method is not allowed.'
              }
              {error === 'Verification' && 
                'Please request a new verification link and try again.'
              }
              {error === 'Configuration' && 
                'Please contact support if this problem persists.'
              }
              {!error && 
                'Please try signing in again. If the problem persists, contact support.'
              }
            </p>
          </div>
          
          <div className="flex flex-col gap-3">
            <Button asChild className="w-full">
              <Link href="/auth/signin">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Link>
            </Button>
            
            <Button variant="outline" asChild className="w-full">
              <Link href="/">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Link>
            </Button>
          </div>

          <div className="text-center pt-4 border-t">
            <p className="text-xs text-gray-500">
              Need help?{' '}
              <Link 
                href="/support" 
                className="text-blue-600 dark:text-blue-400 hover:underline"
              >
                Contact Support
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}