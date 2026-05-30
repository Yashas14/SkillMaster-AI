import { describe, it, expect } from 'vitest';
import {
  cn,
  formatDuration,
  formatNumber,
  formatCurrency,
  slugify,
  getInitials,
  truncate,
  getRelativeTime,
} from '@/lib/utils';

describe('Utils - Extended Tests', () => {
  describe('cn()', () => {
    it('merges conflicting tailwind classes', () => {
      const result = cn('px-2 py-1', 'px-4');
      expect(result).toContain('px-4');
      expect(result).not.toContain('px-2');
    });

    it('handles undefined and null', () => {
      const result = cn('base', undefined, null, 'extra');
      expect(result).toBe('base extra');
    });

    it('handles conditional classes', () => {
      const isActive = true;
      const result = cn('base', isActive && 'active');
      expect(result).toContain('active');
    });
  });

  describe('formatDuration()', () => {
    it('formats minutes to hours and minutes', () => {
      expect(formatDuration(90)).toBe('1h 30m');
    });

    it('formats less than 60 minutes', () => {
      expect(formatDuration(45)).toBe('45m');
    });

    it('formats exactly 60 minutes', () => {
      expect(formatDuration(60)).toBe('1h');
    });

    it('handles zero', () => {
      expect(formatDuration(0)).toBe('0m');
    });
  });

  describe('formatNumber()', () => {
    it('formats thousands with K', () => {
      expect(formatNumber(1500)).toBe('1.5K');
    });

    it('formats millions with M', () => {
      expect(formatNumber(2500000)).toBe('2.5M');
    });

    it('returns small numbers as-is', () => {
      expect(formatNumber(999)).toBe('999');
    });
  });

  describe('formatCurrency()', () => {
    it('formats USD by default', () => {
      const result = formatCurrency(29.99);
      expect(result).toContain('29.99');
    });

    it('handles zero', () => {
      const result = formatCurrency(0);
      expect(result).toContain('0');
    });
  });

  describe('slugify()', () => {
    it('converts text to slug', () => {
      expect(slugify('Hello World')).toBe('hello-world');
    });

    it('removes special characters', () => {
      expect(slugify("What's up? #coding!")).toBe('whats-up-coding');
    });

    it('collapses multiple hyphens', () => {
      expect(slugify('Hello   World')).toBe('hello-world');
    });

    it('trims leading/trailing hyphens', () => {
      expect(slugify(' Hello World ')).toBe('hello-world');
    });
  });

  describe('getInitials()', () => {
    it('gets initials from full name', () => {
      expect(getInitials('John Doe')).toBe('JD');
    });

    it('gets single initial from single name', () => {
      expect(getInitials('Alice')).toBe('A');
    });

    it('handles three-word names', () => {
      const result = getInitials('John Michael Doe');
      expect(result.length).toBeLessThanOrEqual(2);
    });
  });

  describe('truncate()', () => {
    it('truncates long text', () => {
      const long = 'a'.repeat(100);
      const result = truncate(long, 50);
      expect(result.length).toBeLessThanOrEqual(53); // 50 + '...'
      expect(result).toContain('...');
    });

    it('does not truncate short text', () => {
      expect(truncate('short', 50)).toBe('short');
    });
  });

  describe('getRelativeTime()', () => {
    it('returns "just now" for recent dates', () => {
      const now = new Date();
      const result = getRelativeTime(now);
      expect(result).toMatch(/just now|seconds? ago/i);
    });

    it('returns minutes ago for recent past', () => {
      const fiveMinAgo = new Date(Date.now() - 5 * 60 * 1000);
      const result = getRelativeTime(fiveMinAgo);
      expect(result).toBe('5m ago');
    });

    it('returns days ago for past dates', () => {
      const twoDaysAgo = new Date(Date.now() - 2 * 24 * 60 * 60 * 1000);
      const result = getRelativeTime(twoDaysAgo);
      expect(result).toBe('2d ago');
    });
  });
});
