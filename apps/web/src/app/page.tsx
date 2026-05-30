import Link from 'next/link';
import { auth } from '@/lib/auth';
import {
  BookOpen,
  Brain,
  Code2,
  Globe,
  Sparkles,
  TrendingUp,
  Users,
  Zap,
} from 'lucide-react';

export default async function HomePage() {
  const session = await auth();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/80">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white">
              <Brain className="h-5 w-5" />
            </div>
            <span className="text-xl font-bold text-slate-900 dark:text-white">
              SkillMaster <span className="text-brand-600">AI</span>
            </span>
          </Link>

          <div className="hidden items-center gap-8 md:flex">
            <Link
              href="/dashboard/courses"
              className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
            >
              Courses
            </Link>
            <Link
              href="/register"
              className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
            >
              Get Started
            </Link>
            <Link
              href="/login"
              className="text-sm font-medium text-slate-600 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
            >
              Sign In
            </Link>
          </div>

          <div className="flex items-center gap-3">
            {session?.user ? (
              <Link
                href="/dashboard"
                className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700"
              >
                Dashboard
              </Link>
            ) : (
              <>
                <Link
                  href="/login"
                  className="rounded-lg px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                >
                  Sign in
                </Link>
                <Link
                  href="/register"
                  className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700"
                >
                  Get Started Free
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden px-4 pb-20 pt-24 sm:px-6 lg:px-8">
        <div className="absolute inset-0 -z-10">
          <div className="absolute left-1/2 top-0 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-brand-500/10 blur-3xl" />
          <div className="absolute right-0 top-1/4 h-[400px] w-[400px] rounded-full bg-purple-500/10 blur-3xl" />
        </div>

        <div className="mx-auto max-w-5xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 dark:border-brand-800 dark:bg-brand-950 dark:text-brand-300">
            <Sparkles className="h-4 w-4" />
            Powered by Claude Opus 4.6 & GPT-4o
          </div>

          <h1 className="mb-6 text-5xl font-extrabold tracking-tight text-slate-900 sm:text-6xl lg:text-7xl dark:text-white">
            Learn Smarter with{' '}
            <span className="bg-gradient-to-r from-brand-600 to-purple-600 bg-clip-text text-transparent">
              AI-Powered
            </span>{' '}
            Education
          </h1>

          <p className="mx-auto mb-10 max-w-2xl text-lg text-slate-600 dark:text-slate-400">
            Experience the future of learning with personalized AI tutoring, adaptive
            curricula, immersive labs, and blockchain-verified credentials. Master any skill
            3x faster with your AI learning companion.
          </p>

          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/register"
              className="flex items-center gap-2 rounded-xl bg-brand-600 px-8 py-3.5 text-base font-semibold text-white shadow-lg shadow-brand-600/30 transition-all hover:bg-brand-700 hover:shadow-xl"
            >
              <Zap className="h-5 w-5" />
              Start Learning for Free
            </Link>
            <Link
              href="/dashboard/courses"
              className="flex items-center gap-2 rounded-xl border border-slate-300 px-8 py-3.5 text-base font-semibold text-slate-700 transition-all hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              Browse Courses
            </Link>
          </div>

          <div className="mt-12 flex items-center justify-center gap-8 text-sm text-slate-500 dark:text-slate-400">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              <span>50K+ Learners</span>
            </div>
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              <span>500+ Courses</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              <span>4.9/5 Rating</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="border-t border-slate-200 bg-white px-4 py-24 sm:px-6 lg:px-8 dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto max-w-7xl">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-3xl font-bold text-slate-900 sm:text-4xl dark:text-white">
              Everything You Need to Learn Effectively
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-slate-600 dark:text-slate-400">
              Our AI-native platform combines cutting-edge technology with proven learning
              science.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {[
              {
                icon: Brain,
                title: 'AI Tutor',
                description:
                  'Socratic AI tutor that adapts to your learning style with voice, text, and visual explanations.',
                color: 'text-brand-600 bg-brand-50 dark:bg-brand-950',
              },
              {
                icon: Code2,
                title: 'Coding IDE',
                description:
                  'Full-featured browser IDE with AI code review, auto-completion, and real-time execution.',
                color: 'text-green-600 bg-green-50 dark:bg-green-950',
              },
              {
                icon: Globe,
                title: 'XR Learning Labs',
                description:
                  'Immersive 3D virtual labs for chemistry, physics, anatomy, and more with VR support.',
                color: 'text-purple-600 bg-purple-50 dark:bg-purple-950',
              },
              {
                icon: TrendingUp,
                title: 'Adaptive Learning',
                description:
                  'AI-powered curriculum that adapts in real-time based on your progress and learning patterns.',
                color: 'text-orange-600 bg-orange-50 dark:bg-orange-950',
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="group rounded-2xl border border-slate-200 bg-white p-6 transition-all hover:border-slate-300 hover:shadow-lg dark:border-slate-700 dark:bg-slate-800 dark:hover:border-slate-600"
              >
                <div
                  className={`mb-4 inline-flex items-center justify-center rounded-xl p-3 ${feature.color}`}
                >
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-slate-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="border-t border-slate-200 px-4 py-24 sm:px-6 lg:px-8 dark:border-slate-800">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="mb-4 text-3xl font-bold text-slate-900 sm:text-4xl dark:text-white">
            Ready to Transform Your Learning?
          </h2>
          <p className="mb-8 text-lg text-slate-600 dark:text-slate-400">
            Join thousands of learners already using AI to accelerate their education.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-10 py-4 text-lg font-semibold text-white shadow-lg transition-all hover:bg-brand-700"
          >
            <Sparkles className="h-5 w-5" />
            Get Started — It&apos;s Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-slate-50 px-4 py-12 sm:px-6 lg:px-8 dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 md:flex-row">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-brand-600" />
            <span className="font-semibold text-slate-900 dark:text-white">SkillMaster AI</span>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            © {new Date().getFullYear()} SkillMaster AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
