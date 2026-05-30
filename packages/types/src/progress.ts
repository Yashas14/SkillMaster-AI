// ════════════════════════════════════════════════════════════
// Progress tracking types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601, TimestampFields } from './common';

export enum LessonStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
}

export interface LessonProgress extends TimestampFields {
  id: UUID;
  userId: UUID;
  lessonId: UUID;
  courseId: UUID;
  moduleId: UUID;
  status: LessonStatus;
  progressPercent: number;
  videoWatchedSeconds?: number;
  lastPosition?: number;
  completedAt?: ISO8601;
  timeSpentSeconds: number;
  notes?: string;
}

// Quiz types are defined in quiz.ts — imported here for convenience
export type { Quiz, QuizQuestion, QuizOption, QuizAttempt, QuizAnswer } from './quiz';

export interface AssignmentSubmission extends TimestampFields {
  id: UUID;
  userId: UUID;
  assignmentId: UUID;
  courseId: UUID;
  content: string;
  codeSubmission?: string;
  codeLanguage?: string;
  attachments: string[];
  grade?: number;
  maxGrade: number;
  feedback?: string;
  aiFeedback?: string;
  status: 'submitted' | 'grading' | 'graded' | 'returned';
  submittedAt: ISO8601;
  gradedAt?: ISO8601;
  gradedBy?: UUID;
}

export interface StudySession {
  id: UUID;
  userId: UUID;
  courseId?: UUID;
  startedAt: ISO8601;
  endedAt?: ISO8601;
  durationSeconds: number;
  activeDurationSeconds: number;
  lessonsViewed: UUID[];
  quizzesTaken: UUID[];
  xpEarned: number;
  focusScore: number;
}

export interface LearningStreak {
  userId: UUID;
  currentStreak: number;
  longestStreak: number;
  lastStudyDate: ISO8601;
  totalStudyDays: number;
  weeklyGoalMinutes: number;
  weeklyProgressMinutes: number;
}

export interface UpdateLessonProgressInput {
  status?: LessonStatus;
  progressPercent?: number;
  videoWatchedSeconds?: number;
  lastPosition?: number;
  timeSpentSeconds?: number;
  notes?: string;
}
