// ════════════════════════════════════════════════════════════
// Common types used across the platform
// ════════════════════════════════════════════════════════════

export type UUID = string;
export type ISO8601 = string;
export type Email = string;
export type URL = string;

export enum SortDirection {
  ASC = 'asc',
  DESC = 'desc',
}

export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortDirection?: SortDirection;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ApiError;
  timestamp: ISO8601;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface TimestampFields {
  createdAt: ISO8601;
  updatedAt: ISO8601;
}

export interface SoftDeleteFields extends TimestampFields {
  deletedAt?: ISO8601 | null;
}

export type Difficulty = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export type BloomLevel =
  | 'remember'
  | 'understand'
  | 'apply'
  | 'analyze'
  | 'evaluate'
  | 'create';

export type ContentType = 'video' | 'article' | 'quiz' | 'assignment' | 'lab' | 'discussion';

export type MediaType = 'image' | 'video' | 'audio' | 'document' | 'code';
