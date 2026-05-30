// ════════════════════════════════════════════════════════════
// Review types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601 } from './common';

export interface CourseReview {
  id: UUID;
  courseId: UUID;
  userId: UUID;
  userName?: string;
  rating: number;
  title?: string;
  content?: string;
  comment?: string;
  isVerified?: boolean;
  helpfulCount?: number;
  helpful?: number;
  reported?: boolean;
  createdAt: ISO8601;
  updatedAt: ISO8601;
}

export interface CreateCourseReviewRequest {
  courseId: UUID;
  rating: number;
  comment: string;
}

export interface ReviewSummary {
  courseId: UUID;
  averageRating: number;
  totalReviews: number;
  ratingDistribution: Record<number, number>; // 1-5 -> count
}
