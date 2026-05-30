import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useUIStore } from '@/lib/store';

describe('useUIStore', () => {
  beforeEach(() => {
    useUIStore.setState({
      sidebarOpen: true,
      theme: 'system',
      commandPaletteOpen: false,
      notificationsOpen: false,
    });
  });

  it('toggles sidebar', () => {
    const store = useUIStore.getState();
    expect(store.sidebarOpen).toBe(true);

    store.toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(false);

    store.toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(true);
  });

  it('sets theme', () => {
    useUIStore.getState().setTheme('dark');
    expect(useUIStore.getState().theme).toBe('dark');

    useUIStore.getState().setTheme('light');
    expect(useUIStore.getState().theme).toBe('light');
  });

  it('manages command palette state', () => {
    useUIStore.getState().setCommandPaletteOpen(true);
    expect(useUIStore.getState().commandPaletteOpen).toBe(true);

    useUIStore.getState().setCommandPaletteOpen(false);
    expect(useUIStore.getState().commandPaletteOpen).toBe(false);
  });
});
