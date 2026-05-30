'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  Bell,
  BookOpen,
  Brain,
  Code2,
  Compass,
  GraduationCap,
  LayoutDashboard,
  Map,
  Search,
  Settings,
  Trophy,
  BarChart3,
  ChevronLeft,
  LogOut,
} from 'lucide-react';
import { signOut } from 'next-auth/react';
import { useUIStore } from '@/lib/store';
import type { User } from 'next-auth';

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const mainNavItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'My Courses', href: '/dashboard/courses', icon: BookOpen },
  { label: 'AI Tutor', href: '/dashboard/ai-tutor', icon: Brain },
  { label: 'Playground', href: '/dashboard/playground', icon: Code2 },
  { label: 'Learning Paths', href: '/dashboard/learning-paths', icon: Map },
  { label: 'Explore', href: '/courses', icon: Compass },
  { label: 'Search', href: '/dashboard/search', icon: Search },
];

const secondaryNavItems: NavItem[] = [
  { label: 'Leaderboard', href: '/dashboard/leaderboard', icon: Trophy },
  { label: 'Certificates', href: '/dashboard/certificates', icon: GraduationCap },
  { label: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
  { label: 'Notifications', href: '/dashboard/notifications', icon: Bell },
  { label: 'Settings', href: '/dashboard/settings', icon: Settings },
];

interface DashboardSidebarProps {
  user: User;
}

export function DashboardSidebar({ user }: DashboardSidebarProps) {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <aside
      className={cn(
        'relative flex h-full flex-col border-r border-slate-200 bg-white transition-all duration-300 dark:border-slate-800 dark:bg-slate-900',
        sidebarOpen ? 'w-64' : 'w-16',
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between border-b border-slate-200 px-4 dark:border-slate-800">
        {sidebarOpen && (
          <Link href="/" className="flex items-center gap-2">
            <Brain className="h-7 w-7 text-brand-600" />
            <span className="text-lg font-bold text-slate-900 dark:text-white">
              Skill<span className="text-brand-600">Master</span>
            </span>
          </Link>
        )}
        <button
          onClick={toggleSidebar}
          className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300"
        >
          <ChevronLeft
            className={cn('h-5 w-5 transition-transform', !sidebarOpen && 'rotate-180')}
          />
        </button>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        <div className="mb-2">
          {sidebarOpen && (
            <span className="px-3 text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              Main
            </span>
          )}
        </div>
        {mainNavItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white',
                !sidebarOpen && 'justify-center px-0',
              )}
              title={!sidebarOpen ? item.label : undefined}
            >
              <item.icon className="h-5 w-5 shrink-0" />
              {sidebarOpen && <span>{item.label}</span>}
            </Link>
          );
        })}

        <div className="mb-2 mt-6">
          {sidebarOpen && (
            <span className="px-3 text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              More
            </span>
          )}
        </div>
        {secondaryNavItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-50 text-brand-700 dark:bg-brand-950 dark:text-brand-300'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white',
                !sidebarOpen && 'justify-center px-0',
              )}
              title={!sidebarOpen ? item.label : undefined}
            >
              <item.icon className="h-5 w-5 shrink-0" />
              {sidebarOpen && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="border-t border-slate-200 p-3 dark:border-slate-800">
        {sidebarOpen ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700 dark:bg-brand-900 dark:text-brand-300">
                {user.name?.charAt(0) || 'U'}
              </div>
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-slate-900 dark:text-white">
                  {user.name}
                </p>
                <p className="truncate text-xs text-slate-500 dark:text-slate-400">
                  {user.email}
                </p>
              </div>
            </div>
            <button
              onClick={() => signOut({ callbackUrl: '/' })}
              className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950 dark:hover:text-red-400"
              title="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => signOut({ callbackUrl: '/' })}
            className="flex w-full items-center justify-center rounded-lg p-2 text-slate-400 transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950 dark:hover:text-red-400"
            title="Sign out"
          >
            <LogOut className="h-5 w-5" />
          </button>
        )}
      </div>
    </aside>
  );
}
