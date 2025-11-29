// File: frontend/app/auth/signup/page.tsx
// User registration page
// RELEVANT FILES: app/auth/signin/page.tsx, auth.ts

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Chrome, Mail, Eye, EyeOff, Loader2, Pen } from 'lucide-react';

export default function SignUpPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Prepare trimmed values directly for submission
        const trimmedName = name.trim();
        const trimmedEmail = email.trim();

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: trimmedEmail, password, name: trimmedName })
      });

      const data = await response.json();
      if (!response.ok || !data?.success) {
        const message = typeof data?.error === 'string' ? data.error : 'Registration failed. Please try again.';
        throw new Error(message);
      }

      router.push('/auth/signin?registered=true');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed. Please try again.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-900 dark:via-blue-900 dark:to-purple-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center space-y-4 mb-8">
          <div className="flex items-center justify-center">
            <div className="p-3 rounded-full bg-gradient-to-br from-blue-500 to-purple-600">
              <Pen className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 bg-clip-text text-transparent">
            Create Account
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Start creating AI-powered content today
          </p>
        </div>

        <Card className="border-0 shadow-xl bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Sign Up</CardTitle>
            <CardDescription className="text-center">
              Choose your preferred sign-up method
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200">
                {error}
              </div>
            )}

            <Button
              variant="outline"
              className="w-full h-12 border-2"
              disabled={isLoading}
            >
              <Chrome className="h-5 w-5 mr-3 text-blue-600" />
              Sign up with Google
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white dark:bg-gray-900 px-2 text-gray-500">
                  or sign up with email
                </span>
              </div>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-4" autoComplete="on">
              <div className="space-y-2">
                <label htmlFor="name" className="text-sm font-medium">
                  Full Name
                </label>
                <Input
                  id="name"
                  name="name"
                  type="text"
                  placeholder="Enter your name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  autoComplete="name"
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email Address
                </label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                  className="h-12"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Create a password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                    className="h-12 pr-12"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 p-0"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <Button
                type="submit"
                disabled={isLoading || !email || !password || !name}
                className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                ) : (
                  <Mail className="h-5 w-5 mr-2" />
                )}
                Create Account
              </Button>
            </form>

            <div className="text-center text-sm text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Button 
                variant="link" 
                className="p-0 text-blue-600 dark:text-blue-400 font-medium"
                onClick={() => router.push('/auth/signin')}
              >
                Sign in
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
