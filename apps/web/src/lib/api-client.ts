// ════════════════════════════════════════════════════════════
// API Client for FastAPI Backend
// ════════════════════════════════════════════════════════════

import type { ApiResponse, PaginatedResponse, PaginationParams } from '@skillmaster/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;
  private accessToken: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setAccessToken(token: string | null) {
    this.accessToken = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.accessToken) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.accessToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        code: 'UNKNOWN_ERROR',
        message: response.statusText,
      }));

      return {
        success: false,
        error: {
          code: error.code || `HTTP_${response.status}`,
          message: error.message || error.detail || 'An error occurred',
          details: error.details,
        },
        timestamp: new Date().toISOString(),
      };
    }

    const data = await response.json();
    return {
      success: true,
      data,
      timestamp: new Date().toISOString(),
    };
  }

  async get<T>(endpoint: string, params?: Record<string, string>) {
    const searchParams = params ? `?${new URLSearchParams(params)}` : '';
    return this.request<T>(`${endpoint}${searchParams}`);
  }

  async post<T>(endpoint: string, body?: unknown) {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async put<T>(endpoint: string, body?: unknown) {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async patch<T>(endpoint: string, body?: unknown) {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  async delete<T>(endpoint: string) {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  async getPaginated<T>(
    endpoint: string,
    pagination: PaginationParams,
    filters?: Record<string, string>,
  ): Promise<ApiResponse<PaginatedResponse<T>>> {
    const params: Record<string, string> = {
      page: String(pagination.page),
      limit: String(pagination.limit),
      ...filters,
    };
    if (pagination.sortBy) params.sort_by = pagination.sortBy;
    if (pagination.sortDirection) params.sort_direction = pagination.sortDirection;

    return this.get<PaginatedResponse<T>>(endpoint, params);
  }
}

export const apiClient = new ApiClient(API_BASE);
export default apiClient;
