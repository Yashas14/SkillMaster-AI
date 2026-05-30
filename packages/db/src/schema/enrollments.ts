// ════════════════════════════════════════════════════════════
// Database Schema - Enrollments & Progress
// ════════════════════════════════════════════════════════════

import {
  pgTable,
  uuid,
  varchar,
  real,
  integer,
  text,
  timestamp,
  jsonb,
  pgEnum,
  index,
  uniqueIndex,
  boolean,
} from 'drizzle-orm/pg-core';
import { users } from './users';
import { courses, lessons } from './courses';

export const enrollmentStatusEnum = pgEnum('enrollment_status', [
  'active',
  'completed',
  'paused',
  'cancelled',
  'expired',
]);

export const paymentStatusEnum = pgEnum('payment_status', [
  'pending',
  'completed',
  'failed',
  'refunded',
]);

export const lessonStatusEnum = pgEnum('lesson_status', [
  'not_started',
  'in_progress',
  'completed',
]);

export const enrollments = pgTable(
  'enrollments',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    courseId: uuid('course_id')
      .notNull()
      .references(() => courses.id, { onDelete: 'cascade' }),
    status: enrollmentStatusEnum('status').notNull().default('active'),
    enrolledAt: timestamp('enrolled_at', { withTimezone: true }).notNull().defaultNow(),
    completedAt: timestamp('completed_at', { withTimezone: true }),
    expiresAt: timestamp('expires_at', { withTimezone: true }),
    progress: real('progress').notNull().default(0),
    lastAccessedAt: timestamp('last_accessed_at', { withTimezone: true }),
    paymentStatus: paymentStatusEnum('payment_status').notNull().default('completed'),
    paymentId: varchar('payment_id', { length: 255 }),
    amountPaid: real('amount_paid').notNull().default(0),
    currency: varchar('currency', { length: 3 }).notNull().default('USD'),
    certificateId: uuid('certificate_id'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index('enrollments_user_idx').on(table.userId),
    index('enrollments_course_idx').on(table.courseId),
    uniqueIndex('enrollments_user_course_idx').on(table.userId, table.courseId),
    index('enrollments_status_idx').on(table.status),
  ],
);

export const lessonProgress = pgTable(
  'lesson_progress',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    lessonId: uuid('lesson_id')
      .notNull()
      .references(() => lessons.id, { onDelete: 'cascade' }),
    courseId: uuid('course_id')
      .notNull()
      .references(() => courses.id, { onDelete: 'cascade' }),
    moduleId: uuid('module_id').notNull(),
    status: lessonStatusEnum('status').notNull().default('not_started'),
    progressPercent: real('progress_percent').notNull().default(0),
    videoWatchedSeconds: integer('video_watched_seconds'),
    lastPosition: integer('last_position'),
    completedAt: timestamp('completed_at', { withTimezone: true }),
    timeSpentSeconds: integer('time_spent_seconds').notNull().default(0),
    notes: text('notes'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index('progress_user_idx').on(table.userId),
    index('progress_lesson_idx').on(table.lessonId),
    index('progress_course_idx').on(table.courseId),
    uniqueIndex('progress_user_lesson_idx').on(table.userId, table.lessonId),
  ],
);

export const quizzes = pgTable(
  'quizzes',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    courseId: uuid('course_id')
      .notNull()
      .references(() => courses.id, { onDelete: 'cascade' }),
    lessonId: uuid('lesson_id')
      .notNull()
      .references(() => lessons.id, { onDelete: 'cascade' }),
    title: varchar('title', { length: 500 }).notNull(),
    description: text('description').notNull().default(''),
    questions: jsonb('questions').notNull().default([]),
    passingScore: real('passing_score').notNull().default(70),
    maxAttempts: integer('max_attempts').notNull().default(3),
    timeLimitMinutes: integer('time_limit_minutes'),
    shuffleQuestions: boolean('shuffle_questions').notNull().default(false),
    shuffleOptions: boolean('shuffle_options').notNull().default(false),
    showExplanations: boolean('show_explanations').notNull().default(true),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index('quizzes_course_idx').on(table.courseId),
    index('quizzes_lesson_idx').on(table.lessonId),
  ],
);

export const quizAttempts = pgTable(
  'quiz_attempts',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    quizId: uuid('quiz_id')
      .notNull()
      .references(() => quizzes.id, { onDelete: 'cascade' }),
    courseId: uuid('course_id')
      .notNull()
      .references(() => courses.id, { onDelete: 'cascade' }),
    lessonId: uuid('lesson_id')
      .notNull()
      .references(() => lessons.id, { onDelete: 'cascade' }),
    score: real('score').notNull(),
    maxScore: real('max_score').notNull(),
    percentage: real('percentage').notNull(),
    passed: boolean('passed').notNull(),
    answers: jsonb('answers').notNull().default([]),
    timeSpentSeconds: integer('time_spent_seconds').notNull().default(0),
    attemptNumber: integer('attempt_number').notNull().default(1),
    startedAt: timestamp('started_at', { withTimezone: true }).notNull().defaultNow(),
    completedAt: timestamp('completed_at', { withTimezone: true }).notNull().defaultNow(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index('attempts_user_idx').on(table.userId),
    index('attempts_quiz_idx').on(table.quizId),
    index('attempts_course_idx').on(table.courseId),
  ],
);

export const chatSessions = pgTable(
  'chat_sessions',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    courseId: uuid('course_id').references(() => courses.id, { onDelete: 'set null' }),
    lessonId: uuid('lesson_id').references(() => lessons.id, { onDelete: 'set null' }),
    title: varchar('title', { length: 500 }).notNull().default('New Chat'),
    persona: varchar('persona', { length: 50 }).notNull().default('socratic_guide'),
    summary: text('summary'),
    isActive: boolean('is_active').notNull().default(true),
    messageCount: integer('message_count').notNull().default(0),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index('chats_user_idx').on(table.userId),
    index('chats_course_idx').on(table.courseId),
    index('chats_active_idx').on(table.isActive),
  ],
);

export const chatMessages = pgTable(
  'chat_messages',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    sessionId: uuid('session_id')
      .notNull()
      .references(() => chatSessions.id, { onDelete: 'cascade' }),
    role: varchar('role', { length: 20 }).notNull(),
    content: text('content').notNull(),
    contentType: varchar('content_type', { length: 20 }).notNull().default('text'),
    metadata: jsonb('metadata').default({}),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index('messages_session_idx').on(table.sessionId),
    index('messages_created_idx').on(table.createdAt),
  ],
);
