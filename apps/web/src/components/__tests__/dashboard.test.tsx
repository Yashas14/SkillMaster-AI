import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => '/dashboard',
  useSearchParams: () => new URLSearchParams(),
}));

// Mock next-auth
vi.mock('next-auth/react', () => ({
  useSession: () => ({
    data: {
      user: {
        id: 'user-1',
        name: 'Test User',
        email: 'test@example.com',
        role: 'student',
        image: null,
      },
    },
    status: 'authenticated',
  }),
  signIn: vi.fn(),
  signOut: vi.fn(),
  SessionProvider: ({ children }: { children: React.ReactNode }) => children,
}));

describe('Dashboard Components', () => {
  describe('Sidebar', () => {
    it('renders main navigation items', async () => {
      const { DashboardSidebar } = await import('@/components/dashboard/sidebar');
      const user = { id: 'user-1', name: 'Test User', email: 'test@example.com' };
      render(<DashboardSidebar user={user} />);
      
      expect(screen.getByText('Dashboard')).toBeDefined();
      expect(screen.getByText('My Courses')).toBeDefined();
      expect(screen.getByText('AI Tutor')).toBeDefined();
    });

    it('renders Phase 2-4 navigation items', async () => {
      const { DashboardSidebar } = await import('@/components/dashboard/sidebar');
      const user = { id: 'user-1', name: 'Test User', email: 'test@example.com' };
      render(<DashboardSidebar user={user} />);
      
      expect(screen.getByText('Playground')).toBeDefined();
      expect(screen.getByText('Learning Paths')).toBeDefined();
      expect(screen.getByText('Leaderboard')).toBeDefined();
      expect(screen.getByText('Certificates')).toBeDefined();
      expect(screen.getByText('Analytics')).toBeDefined();
      expect(screen.getByText('Notifications')).toBeDefined();
      expect(screen.getByText('Settings')).toBeDefined();
    });

    it('renders user name', async () => {
      const { DashboardSidebar } = await import('@/components/dashboard/sidebar');
      const user = { id: 'user-1', name: 'Test User', email: 'test@example.com' };
      render(<DashboardSidebar user={user} />);
      
      expect(screen.getByText('Test User')).toBeDefined();
    });
  });
});
