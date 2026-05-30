import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
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

// Mock next-auth/react
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
      accessToken: 'mock-token',
    },
    status: 'authenticated',
  }),
  signOut: vi.fn(),
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => React.createElement('a', { href }, children),
}));

// Mock next/image
vi.mock('next/image', () => ({
  default: (props: Record<string, unknown>) =>
    React.createElement('img', { ...props }),
}));

import { DashboardHeader } from '@/components/dashboard/header';

const mockUser = {
  id: 'user-1',
  name: 'Test User',
  email: 'test@example.com',
  image: null,
};

describe('Dashboard Header', () => {
  it('renders the search button', () => {
    render(<DashboardHeader user={mockUser} />);
    const searchButton = screen.getByText(/search courses/i);
    expect(searchButton).toBeDefined();
  });

  it('renders notification bell button', () => {
    render(<DashboardHeader user={mockUser} />);
    const notifButton = screen.getByTitle('Notifications');
    expect(notifButton).toBeDefined();
  });

  it('renders theme toggle button', () => {
    render(<DashboardHeader user={mockUser} />);
    const themeButton = screen.getByTitle('Toggle theme');
    expect(themeButton).toBeDefined();
  });
});
