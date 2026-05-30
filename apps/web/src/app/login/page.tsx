'use client';

import { useState } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Brain, Chrome, Github, Loader2, Mail } from 'lucide-react';
import { toast } from 'sonner';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  async function onSubmit(data: LoginFormData) {
    setIsLoading(true);
    try {
      const result = await signIn('credentials', {
        email: data.email,
        password: data.password,
        redirect: false,
      });

      if (result?.error) {
        toast.error('Invalid email or password');
      } else {
        router.push('/dashboard');
        router.refresh();
      }
    } catch {
      toast.error('Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleOAuthLogin(provider: string) {
    setOauthLoading(provider);
    try {
      await signIn(provider, { callbackUrl: '/dashboard' });
    } catch {
      toast.error(`Failed to sign in with ${provider}`);
      setOauthLoading(null);
    }
  }

  return (
    <div className="flex min-h-screen">
      {/* Left Side - Branding */}
      <div className="relative hidden w-1/2 items-center justify-center bg-gradient-to-br from-brand-600 via-brand-700 to-purple-800 lg:flex">
        <div className="max-w-md px-8 text-center">
          <div className="mb-6 flex justify-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/20 backdrop-blur">
              <Brain className="h-10 w-10 text-white" />
            </div>
          </div>
          <h2 className="mb-4 text-3xl font-bold text-white">Welcome Back</h2>
          <p className="text-lg text-brand-100">
            Continue your learning journey with AI-powered personalized education. Your AI
            tutor is ready to help you master new skills.
          </p>
          <div className="mt-8 grid grid-cols-3 gap-4 text-center text-sm text-brand-200">
            <div>
              <div className="text-2xl font-bold text-white">50K+</div>
              <div>Learners</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">500+</div>
              <div>Courses</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">98%</div>
              <div>Satisfaction</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex w-full flex-col justify-center px-8 sm:px-12 lg:w-1/2 lg:px-16">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8 flex items-center gap-2 lg:hidden">
            <Brain className="h-8 w-8 text-brand-600" />
            <span className="text-xl font-bold">SkillMaster AI</span>
          </div>

          <h1 className="mb-2 text-2xl font-bold text-slate-900 dark:text-white">Sign in</h1>
          <p className="mb-8 text-slate-600 dark:text-slate-400">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="font-medium text-brand-600 hover:text-brand-700">
              Sign up for free
            </Link>
          </p>

          {/* OAuth Buttons */}
          <div className="mb-6 grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => handleOAuthLogin('google')}
              disabled={!!oauthLoading}
              className="flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              {oauthLoading === 'google' ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Chrome className="h-4 w-4" />
              )}
              Google
            </button>
            <button
              type="button"
              onClick={() => handleOAuthLogin('github')}
              disabled={!!oauthLoading}
              className="flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              {oauthLoading === 'github' ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Github className="h-4 w-4" />
              )}
              GitHub
            </button>
          </div>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200 dark:border-slate-700" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-4 text-slate-500 dark:bg-slate-900 dark:text-slate-400">
                or continue with email
              </span>
            </div>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
              >
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  {...register('email')}
                  className="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-10 pr-4 text-sm outline-none transition-colors focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                  placeholder="you@example.com"
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>
              )}
            </div>

            <div>
              <div className="mb-1.5 flex items-center justify-between">
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-slate-700 dark:text-slate-300"
                >
                  Password
                </label>
                <Link
                  href="/forgot-password"
                  className="text-xs font-medium text-brand-600 hover:text-brand-700"
                >
                  Forgot password?
                </Link>
              </div>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                {...register('password')}
                className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition-colors focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
