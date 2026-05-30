// ════════════════════════════════════════════════════════════
// Enrollment types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601, TimestampFields } from './common';

export enum EnrollmentStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  PAUSED = 'paused',
  CANCELLED = 'cancelled',
  EXPIRED = 'expired',
}

export enum PaymentStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  FAILED = 'failed',
  REFUNDED = 'refunded',
}

export interface Enrollment extends TimestampFields {
  id: UUID;
  userId: UUID;
  courseId: UUID;
  status: EnrollmentStatus;
  enrolledAt: ISO8601;
  completedAt?: ISO8601;
  expiresAt?: ISO8601;
  progress: number;
  lastAccessedAt?: ISO8601;
  paymentStatus: PaymentStatus;
  paymentId?: string;
  amountPaid: number;
  currency: string;
  certificateId?: UUID;
}

export interface CreateEnrollmentInput {
  userId: UUID;
  courseId: UUID;
  paymentId?: string;
  amountPaid?: number;
  currency?: string;
}

export interface EnrollmentWithCourse extends Enrollment {
  course: {
    id: UUID;
    title: string;
    slug: string;
    thumbnailUrl?: string;
    instructorName: string;
    totalLessons: number;
    estimatedDurationMinutes: number;
  };
}
