// frontend/app/auth/error/page.tsx

import { Suspense } from 'react';
import { AuthErrorContent } from './error-content';

export default function AuthErrorPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-linear-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-blue-900 dark:to-purple-900 flex items-center justify-center p-4">
        <div className="text-center">Loading...</div>
      </div>
    }>
      <AuthErrorContent />
    </Suspense>
  );
}