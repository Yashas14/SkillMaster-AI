'use client';

import { Bell, Search, Moon, Sun } from 'lucide-react';
import { useUIStore } from '@/lib/store';
import type { User } from 'next-auth';

interface DashboardHeaderProps {
  user: User;
}

export function DashboardHeader({ user }: DashboardHeaderProps) {
  const { theme, setTheme, setCommandPaletteOpen } = useUIStore();

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
    document.documentElement.classList.toggle('dark');
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 dark:border-slate-800 dark:bg-slate-900">
      {/* Search Bar */}
      <button
        onClick={() => setCommandPaletteOpen(true)}
        className="flex items-center gap-3 rounded-lg bg-slate-100 px-4 py-2 text-sm text-slate-500 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:hover:bg-slate-700"
      >
        <Search className="h-4 w-4" />
        <span>Search courses, lessons, topics...</span>
        <kbd className="ml-8 hidden rounded border border-slate-300 bg-white px-1.5 py-0.5 text-xs text-slate-400 sm:inline dark:border-slate-600 dark:bg-slate-700">
          ⌘K
        </kbd>
      </button>

      {/* Right Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
          title="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>

        <button
          className="relative rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
          title="Notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-red-500" />
        </button>

        <div className="ml-2 flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700 dark:bg-brand-900 dark:text-brand-300">
          {user.name?.charAt(0) || 'U'}
        </div>
      </div>
    </header>
  );
}
