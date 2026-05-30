// ════════════════════════════════════════════════════════════
// Auth types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601, Email, UserRole } from './index';

export interface AuthUser {
  id: UUID;
  email: Email;
  name: string;
  role: UserRole;
  avatarUrl?: string;
  isVerified: boolean;
}

export interface LoginCredentials {
  email: Email;
  password: string;
}

export interface RegisterInput {
  email: Email;
  name: string;
  password: string;
  role?: UserRole;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: ISO8601;
}

export interface JWTPayload {
  sub: UUID;
  email: Email;
  role: UserRole;
  iat: number;
  exp: number;
}

export interface PasswordResetRequest {
  email: Email;
}

export interface PasswordResetConfirm {
  token: string;
  newPassword: string;
}

export interface OAuthProfile {
  provider: string;
  providerId: string;
  email: Email;
  name: string;
  avatarUrl?: string;
}
