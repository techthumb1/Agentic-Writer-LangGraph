// File: frontend/app/auth/signin/page.tsx
'use client';

import { useState, useMemo, useCallback, FormEvent } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { signIn } from 'next-auth/react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Checkbox } from '@/components/ui/checkbox';
import { Chrome, Mail, Loader2, Sparkles, Lock, Eye, EyeOff } from 'lucide-react';

export default function SignInPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Derived params
  const callbackUrl = useMemo(() => searchParams.get('callbackUrl') || '/', [searchParams]);
  const error = useMemo(() => searchParams.get('error') || '', [searchParams]);
  const initialEmail = useMemo(() => searchParams.get('email') || '', [searchParams]);

  // State
  const [email, setEmail] = useState<string>(initialEmail);
  const [password, setPassword] = useState<string>('');
  const [remember, setRemember] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState(false);
  const [emailIsLoading, setEmailIsLoading] = useState(false);
  const [credIsLoading, setCredIsLoading] = useState(false);
  const [message, setMessage] = useState<string>('');
  const [showPassword, setShowPassword] = useState(false);

  // Utils
  const isValidEmail = (val: string) => /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(val);

  // OAuth (Google)
  const handleGoogleSignIn = useCallback(async () => {
    try {
      setIsLoading(true);
      await signIn('google', { callbackUrl });
    } finally {
      setIsLoading(false);
    }
  }, [callbackUrl]);

  // Magic-link (Email provider)
  const handleEmailSignIn = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      setMessage('');
      if (!email || !isValidEmail(email)) {
        setMessage('Please enter a valid email address.');
        return;
      }
      try {
        setEmailIsLoading(true);
        const res = await signIn('email', { email, callbackUrl, redirect: false });
        if (res?.ok) {
          setMessage('Check your inbox for a sign-in link.');
        } else {
          setMessage('Unable to send sign-in link. Please try again.');
        }
      } catch {
        setMessage('An unexpected error occurred. Try again.');
      } finally {
        setEmailIsLoading(false);
      }
    },
    [email, callbackUrl]
  );

  // Credentials (Email + Password)
  const handleCredentialsSignIn = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      setMessage('');
      // Basic validation
      if (!email || !isValidEmail(email)) {
        setMessage('Please enter a valid email address.');
        return;
      }
      if (!password || password.length < 6) {
        setMessage('Please enter your password (min 6 characters).');
        return;
      }

      try {
        setCredIsLoading(true);
        const res = await signIn('credentials', {
          email,
          password,
          // Some setups expect username/password; ensure your CredentialsProvider matches these keys
          redirect: false,
          callbackUrl
        });

        if (res?.ok) {
          // Optional: persist "remember me" via your own cookie logic
          // NextAuth session duration is configured server-side.
          router.push(callbackUrl);
        } else {
          setMessage(res?.error || 'Invalid credentials. Please try again.');
        }
      } catch {
        setMessage('Unable to sign in with credentials right now.');
      } finally {
        setCredIsLoading(false);
      }
    },
    [email, password, callbackUrl, router]
  );

  return (
    <div className="min-h-[calc(100vh-4rem)] w-full grid place-items-center px-4 py-10">
      <div className="w-full max-w-md">
        <Card className="shadow-lg">
          <CardHeader className="space-y-2 text-center">
            <CardTitle className="text-2xl font-semibold">Welcome back</CardTitle>
            <CardDescription>Sign in to continue to WriterzRoom</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Error passed via query */}
            {error && (
              <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md border border-red-200 dark:bg-red-950/20 dark:text-red-300 dark:border-red-900">
                {error}
              </div>
            )}
            {/* Inline status */}
            {message && !error && (
              <div className="p-3 text-sm text-blue-700 bg-blue-50 rounded-md border border-blue-200 dark:bg-blue-950/20 dark:text-blue-300 dark:border-blue-900">
                {message}
              </div>
            )}

            {/* OAuth */}
            <div className="grid gap-3">
              <Button
                type="button"
                variant="outline"
                className="w-full"
                onClick={handleGoogleSignIn}
                disabled={isLoading}
              >
                {isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Chrome className="h-4 w-4 mr-2" />}
                Continue with Google
              </Button>
            </div>

            <div className="relative my-2">
              <Separator />
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-background px-2 text-xs text-muted-foreground">
                or
              </span>
            </div>

            {/* Magic link */}
            <form className="grid gap-4" onSubmit={handleEmailSignIn} noValidate>
              <div className="grid gap-2">
                <Label htmlFor="email-magic">Email (magic link)</Label>
                <Input
                  id="email-magic"
                  type="email"
                  inputMode="email"
                  autoComplete="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={emailIsLoading}>
                {emailIsLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Mail className="mr-2 h-4 w-4" />}
                Send magic link
              </Button>
            </form>

            <div className="relative my-2">
              <Separator />
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-background px-2 text-xs text-muted-foreground">
                or sign in with password
              </span>
            </div>

            {/* Credentials */}
            <form className="grid gap-4" onSubmit={handleCredentialsSignIn} noValidate>
              <div className="grid gap-2">
                <Label htmlFor="email-cred">Email</Label>
                <Input
                  id="email-cred"
                  type="email"
                  inputMode="email"
                  autoComplete="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    placeholder="Your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                  <button
                    type="button"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    className="absolute inset-y-0 right-2 flex items-center"
                    onClick={() => setShowPassword((s) => !s)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Checkbox
                    id="remember"
                    checked={remember}
                    onCheckedChange={(v) => setRemember(Boolean(v))}
                  />
                  <Label htmlFor="remember" className="text-sm text-muted-foreground">
                    Remember me
                  </Label>
                </div>

                <Button
                  variant="link"
                  type="button"
                  className="px-0 text-xs"
                  onClick={() => router.push('/auth/reset')}
                >
                  Forgot password?
                </Button>
              </div>

              <Button type="submit" className="w-full" disabled={credIsLoading}>
                {credIsLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Lock className="mr-2 h-4 w-4" />
                )}
                Sign in
              </Button>
            </form>

            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>By continuing you agree to our Terms & Privacy.</span>
              <Button
                variant="link"
                className="px-0 text-xs"
                type="button"
                onClick={() => router.push('/auth/signup')}
              >
                Create account
              </Button>
            </div>
          </CardContent>
        </Card>

        <div className="mt-6 text-center space-y-3">
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <Sparkles className="h-4 w-4" />
            <span>AI-powered content creation platform</span>
          </div>
          <div className="grid grid-cols-3 gap-4 text-xs text-muted-foreground">
            <div>Smart Templates</div>
            <div>Fast Generation</div>
            <div>Style Profiles</div>
          </div>
        </div>
      </div>
    </div>
  );
}
