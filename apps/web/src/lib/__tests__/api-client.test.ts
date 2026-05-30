import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiClient } from '@/lib/api-client';

// Mock global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('apiClient', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('makes GET requests with correct URL', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'test' }),
    });

    await apiClient.get('/api/v1/courses');
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/courses'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      }),
    );
  });

  it('makes POST requests with body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: '1' }),
    });

    const body = { title: 'Test Course' };
    await apiClient.post('/api/v1/courses', body);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/courses'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(body),
      }),
    );
  });

  it('includes authorization header when token set', async () => {
    apiClient.setAccessToken('test-token');
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: 'secure' }),
    });

    await apiClient.get('/api/v1/auth/me');
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/auth/me'),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer test-token',
        }),
      }),
    );
    apiClient.setAccessToken(null);
  });

  it('returns error response on non-OK responses', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      json: async () => ({ detail: 'Not found' }),
    });

    const result = await apiClient.get('/api/v1/courses/nonexistent');
    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
  });

  it('makes DELETE requests', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    await apiClient.delete('/api/v1/courses/1');
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/courses/1'),
      expect.objectContaining({ method: 'DELETE' }),
    );
  });

  it('makes PATCH requests', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ updated: true }),
    });

    const body = { title: 'Updated Course' };
    await apiClient.patch('/api/v1/courses/1', body);
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/courses/1'),
      expect.objectContaining({
        method: 'PATCH',
        body: JSON.stringify(body),
      }),
    );
  });
});
