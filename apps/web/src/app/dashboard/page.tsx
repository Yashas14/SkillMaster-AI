import { auth } from '@/lib/auth';
import { redirect } from 'next/navigation';
import {
  BookOpen,
  Clock,
  Flame,
  Trophy,
  TrendingUp,
  Target,
} from 'lucide-react';
import Link from 'next/link';

export const metadata = {
  title: 'Dashboard',
};

export default async function DashboardPage() {
  const session = await auth();
  if (!session?.user) redirect('/login');

  const user = session.user;
  const firstName = user.name?.split(' ')[0] || 'Learner';

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Welcome back, {firstName}! 👋
          </h1>
          <p className="mt-1 text-slate-600 dark:text-slate-400">
            Continue your learning journey. Your AI tutor is ready.
          </p>
        </div>
        <Link
          href="/dashboard/ai-tutor"
          className="flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-700"
        >
          <Target className="h-4 w-4" />
          Ask AI Tutor
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            label: 'Courses Enrolled',
            value: '5',
            change: '+2 this month',
            icon: BookOpen,
            color: 'text-brand-600 bg-brand-50 dark:bg-brand-950',
          },
          {
            label: 'Study Streak',
            value: '12 days',
            change: 'Keep it up!',
            icon: Flame,
            color: 'text-orange-600 bg-orange-50 dark:bg-orange-950',
          },
          {
            label: 'XP Earned',
            value: '2,450',
            change: '+350 this week',
            icon: Trophy,
            color: 'text-yellow-600 bg-yellow-50 dark:bg-yellow-950',
          },
          {
            label: 'Hours Learned',
            value: '48.5',
            change: '+6.2 this week',
            icon: Clock,
            color: 'text-green-600 bg-green-50 dark:bg-green-950',
          },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900"
          >
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
                {stat.label}
              </p>
              <div className={`rounded-lg p-2 ${stat.color}`}>
                <stat.icon className="h-4 w-4" />
              </div>
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
              {stat.value}
            </p>
            <p className="mt-1 flex items-center gap-1 text-xs text-green-600">
              <TrendingUp className="h-3 w-3" />
              {stat.change}
            </p>
          </div>
        ))}
      </div>

      {/* Continue Learning */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">
          Continue Learning
        </h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[
            {
              title: 'Full-Stack AI Development',
              instructor: 'Dr. Sarah Chen',
              progress: 25,
              nextLesson: 'Understanding the Claude API',
              thumbnail: '/api/placeholder/400/200',
            },
            {
              title: 'Intro to Machine Learning',
              instructor: 'Dr. Sarah Chen',
              progress: 10,
              nextLesson: 'Linear Regression Basics',
              thumbnail: '/api/placeholder/400/200',
            },
          ].map((course) => (
            <Link
              key={course.title}
              href="/dashboard/courses"
              className="group overflow-hidden rounded-xl border border-slate-200 bg-white transition-all hover:border-slate-300 hover:shadow-md dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700"
            >
              <div className="aspect-video bg-gradient-to-br from-brand-500 to-purple-600 p-4">
                <span className="rounded-md bg-white/20 px-2 py-1 text-xs font-medium text-white backdrop-blur">
                  {course.progress}% complete
                </span>
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-slate-900 group-hover:text-brand-600 dark:text-white dark:group-hover:text-brand-400">
                  {course.title}
                </h3>
                <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  {course.instructor}
                </p>
                <div className="mt-3">
                  <div className="mb-1.5 flex items-center justify-between text-xs">
                    <span className="text-slate-500">Progress</span>
                    <span className="font-medium text-brand-600">{course.progress}%</span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
                    <div
                      className="h-full rounded-full bg-brand-600 transition-all"
                      style={{ width: `${course.progress}%` }}
                    />
                  </div>
                </div>
                <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
                  Next: {course.nextLesson}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">
          Quick Actions
        </h2>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {[
            { label: 'AI Tutor', href: '/dashboard/ai-tutor', icon: '🤖' },
            { label: 'Coding IDE', href: '/dashboard/ide', icon: '💻' },
            { label: 'Browse Courses', href: '/courses', icon: '📚' },
            { label: 'Leaderboard', href: '/dashboard/leaderboard', icon: '🏆' },
          ].map((action) => (
            <Link
              key={action.label}
              href={action.href}
              className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 transition-all hover:border-brand-300 hover:shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:hover:border-slate-700"
            >
              <span className="text-2xl">{action.icon}</span>
              <span className="font-medium text-slate-900 dark:text-white">{action.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
