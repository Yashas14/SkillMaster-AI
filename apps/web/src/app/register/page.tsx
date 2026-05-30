'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Brain, Loader2, Mail, User } from 'lucide-react';
import { toast } from 'sonner';
import apiClient from '@/lib/api-client';

const registerSchema = z
  .object({
    name: z.string().min(2, 'Name must be at least 2 characters'),
    email: z.string().email('Please enter a valid email'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Must contain at least one number'),
    confirmPassword: z.string(),
    role: z.enum(['student', 'instructor']),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: { role: 'student' },
  });

  async function onSubmit(data: RegisterFormData) {
    setIsLoading(true);
    try {
      const result = await apiClient.post('/api/v1/auth/register', {
        name: data.name,
        email: data.email,
        password: data.password,
        role: data.role,
      });

      if (result.success) {
        toast.success('Account created! Please sign in.');
        router.push('/login');
      } else {
        toast.error(result.error?.message || 'Registration failed');
      }
    } catch {
      toast.error('Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-slate-50 to-white px-4 dark:from-slate-950 dark:to-slate-900">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <Link href="/" className="mb-6 inline-flex items-center gap-2">
            <Brain className="h-8 w-8 text-brand-600" />
            <span className="text-xl font-bold text-slate-900 dark:text-white">
              SkillMaster AI
            </span>
          </Link>
          <h1 className="mb-2 text-2xl font-bold text-slate-900 dark:text-white">
            Create your account
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-brand-600 hover:text-brand-700">
              Sign in
            </Link>
          </p>
        </div>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-4 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900"
        >
          <div>
            <label
              htmlFor="name"
              className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Full name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                id="name"
                type="text"
                {...register('name')}
                className="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-10 pr-4 text-sm outline-none transition-colors focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                placeholder="John Doe"
              />
            </div>
            {errors.name && <p className="mt-1 text-xs text-red-500">{errors.name.message}</p>}
          </div>

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
            <label
              htmlFor="password"
              className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              {...register('password')}
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition-colors focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              placeholder="••••••••"
            />
            {errors.password && (
              <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>
            )}
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              Confirm password
            </label>
            <input
              id="confirmPassword"
              type="password"
              {...register('confirmPassword')}
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition-colors focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
              placeholder="••••••••"
            />
            {errors.confirmPassword && (
              <p className="mt-1 text-xs text-red-500">{errors.confirmPassword.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              I want to
            </label>
            <div className="grid grid-cols-2 gap-3">
              <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-slate-300 p-3 transition-colors has-[:checked]:border-brand-500 has-[:checked]:bg-brand-50 dark:border-slate-700 dark:has-[:checked]:border-brand-500 dark:has-[:checked]:bg-brand-950">
                <input type="radio" value="student" {...register('role')} className="accent-brand-600" />
                <span className="text-sm font-medium">Learn</span>
              </label>
              <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-slate-300 p-3 transition-colors has-[:checked]:border-brand-500 has-[:checked]:bg-brand-50 dark:border-slate-700 dark:has-[:checked]:border-brand-500 dark:has-[:checked]:bg-brand-950">
                <input
                  type="radio"
                  value="instructor"
                  {...register('role')}
                  className="accent-brand-600"
                />
                <span className="text-sm font-medium">Teach</span>
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating account...
              </>
            ) : (
              'Create account'
            )}
          </button>

          <p className="text-center text-xs text-slate-500 dark:text-slate-400">
            By creating an account, you agree to our{' '}
            <Link href="/terms" className="text-brand-600 hover:underline">
              Terms of Service
            </Link>{' '}
            and{' '}
            <Link href="/privacy" className="text-brand-600 hover:underline">
              Privacy Policy
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
