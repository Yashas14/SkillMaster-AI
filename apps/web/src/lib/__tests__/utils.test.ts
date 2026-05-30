import { describe, it, expect } from 'vitest';
import { cn, formatDuration, formatNumber, formatCurrency, slugify, getInitials, truncate } from '@/lib/utils';

describe('cn utility', () => {
  it('merges class names correctly', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('handles conditional classes', () => {
    expect(cn('base', false && 'hidden', true && 'visible')).toBe('base visible');
  });

  it('merges tailwind classes without conflicts', () => {
    expect(cn('px-2 py-1', 'px-4')).toBe('py-1 px-4');
  });
});

describe('formatDuration', () => {
  it('formats minutes under 60', () => {
    expect(formatDuration(45)).toBe('45m');
  });

  it('formats exact hours', () => {
    expect(formatDuration(120)).toBe('2h');
  });

  it('formats hours and minutes', () => {
    expect(formatDuration(90)).toBe('1h 30m');
  });
});

describe('formatNumber', () => {
  it('formats numbers under 1000', () => {
    expect(formatNumber(500)).toBe('500');
  });

  it('formats thousands', () => {
    expect(formatNumber(1500)).toBe('1.5K');
  });

  it('formats millions', () => {
    expect(formatNumber(2500000)).toBe('2.5M');
  });
});

describe('formatCurrency', () => {
  it('formats USD', () => {
    expect(formatCurrency(49.99)).toBe('$49.99');
  });

  it('formats free courses', () => {
    expect(formatCurrency(0)).toBe('$0');
  });
});

describe('slugify', () => {
  it('converts title to slug', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('handles special characters', () => {
    expect(slugify("What's New in React 19?")).toBe('whats-new-in-react-19');
  });

  it('removes leading/trailing dashes', () => {
    expect(slugify('--hello--')).toBe('hello');
  });
});

describe('getInitials', () => {
  it('gets initials from full name', () => {
    expect(getInitials('John Doe')).toBe('JD');
  });

  it('handles single name', () => {
    expect(getInitials('John')).toBe('J');
  });

  it('limits to 2 initials', () => {
    expect(getInitials('John Michael Doe')).toBe('JM');
  });
});

describe('truncate', () => {
  it('truncates long text', () => {
    expect(truncate('Hello World', 5)).toBe('Hello...');
  });

  it('returns short text unchanged', () => {
    expect(truncate('Hi', 10)).toBe('Hi');
  });
});
