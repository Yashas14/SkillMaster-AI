// ════════════════════════════════════════════════════════════
// Database Schema - Courses
// ════════════════════════════════════════════════════════════

import {
  pgTable,
  uuid,
  varchar,
  text,
  boolean,
  integer,
  real,
  timestamp,
  jsonb,
  pgEnum,
  index,
  uniqueIndex,
} from 'drizzle-orm/pg-core';
import { users } from './users';

export const courseStatusEnum = pgEnum('course_status', [
  'draft',
  'review',
  'published',
  'archived',
]);

export const courseCategoryEnum = pgEnum('course_category', [
  'programming',
  'data_science',
  'web_development',
  'mobile_development',
  'ai_ml',
  'devops',
  'design',
  'business',
  'science',
  'mathematics',
  'language',
  'other',
]);

export const difficultyEnum = pgEnum('difficulty', [
  'beginner',
  'intermediate',
  'advanced',
  'expert',
]);

export const contentTypeEnum = pgEnum('content_type', [
  'video',
  'article',
  'quiz',
  'assignment',
  'lab',
  'discussion',
]);

export const bloomLevelEnum = pgEnum('bloom_level', [
  'remember',
  'understand',
  'apply',
  'analyze',
  'evaluate',
  'create',
]);

export const courses = pgTable(
  'courses',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    title: varchar('title', { length: 500 }).notNull(),
    slug: varchar('slug', { length: 600 }).notNull().unique(),
    description: text('description').notNull(),
    shortDescription: varchar('short_description', { length: 500 }).notNull(),
    instructorId: uuid('instructor_id')
      .notNull()
      .references(() => users.id, { onDelete: 'restrict' }),
    thumbnailUrl: text('thumbnail_url'),
    previewVideoUrl: text('preview_video_url'),
    category: courseCategoryEnum('category').notNull(),
    subcategory: varchar('subcategory', { length: 255 }),
    tags: jsonb('tags').notNull().default([]),
    difficulty: difficultyEnum('difficulty').notNull().default('beginner'),
    language: varchar('language', { length: 10 }).notNull().default('en'),
    status: courseStatusEnum('status').notNull().default('draft'),
    price: real('price').notNull().default(0),
    currency: varchar('currency', { length: 3 }).notNull().default('USD'),
    isFree: boolean('is_free').notNull().default(true),
    estimatedDurationMinutes: integer('estimated_duration_minutes').notNull().default(0),
    totalLessons: integer('total_lessons').notNull().default(0),
    totalModules: integer('total_modules').notNull().default(0),
    rating: real('rating').notNull().default(0),
    totalRatings: integer('total_ratings').notNull().default(0),
    totalEnrollments: integer('total_enrollments').notNull().default(0),
    prerequisites: jsonb('prerequisites').notNull().default([]),
    learningOutcomes: jsonb('learning_outcomes').notNull().default([]),
    targetAudience: jsonb('target_audience').notNull().default([]),
    metadata: jsonb('metadata').notNull().default({}),
    publishedAt: timestamp('published_at', { withTimezone: true }),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
    deletedAt: timestamp('deleted_at', { withTimezone: true }),
  },
  (table) => [
    uniqueIndex('courses_slug_idx').on(table.slug),
    index('courses_instructor_idx').on(table.instructorId),
    index('courses_status_idx').on(table.status),
    index('courses_category_idx').on(table.category),
    index('courses_difficulty_idx').on(table.difficulty),
    index('courses_rating_idx').on(table.rating),
    index('courses_created_at_idx').on(table.createdAt),
  ],
);

export const courseModules = pgTable(
  'course_modules',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    courseId: uuid('course_id')
      .notNull()
      .references(() => courses.id, { onDelete: 'cascade' }),
    title: varchar('title', { length: 500 }).notNull(),
    description: text('description').notNull().default(''),
    order: integer('order').notNull(),
    estimatedDurationMinutes: integer('estimated_duration_minutes').notNull().default(0),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index('modules_course_idx').on(table.courseId),
    index('modules_order_idx').on(table.courseId, table.order),
  ],
);

export const lessons = pgTable(
  'lessons',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    moduleId: uuid('module_id')
      .notNull()
      .references(() => courseModules.id, { onDelete: 'cascade' }),
    courseId: uuid('course_id')
      .notNull()
      .references(() => courses.id, { onDelete: 'cascade' }),
    title: varchar('title', { length: 500 }).notNull(),
    description: text('description').notNull().default(''),
    contentType: contentTypeEnum('content_type').notNull(),
    order: integer('order').notNull(),
    estimatedDurationMinutes: integer('estimated_duration_minutes').notNull().default(0),
    isFree: boolean('is_free').notNull().default(false),
    isRequired: boolean('is_required').notNull().default(true),
    bloomLevel: bloomLevelEnum('bloom_level').notNull().default('remember'),
    content: jsonb('content').notNull().default({}),
    resources: jsonb('resources').notNull().default([]),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index('lessons_module_idx').on(table.moduleId),
    index('lessons_course_idx').on(table.courseId),
    index('lessons_order_idx').on(table.moduleId, table.order),
  ],
);

export const courseReviews = pgTable(
  'course_reviews',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    courseId: uuid('course_id')
      .notNull()
      .references(() => courses.id, { onDelete: 'cascade' }),
    userId: uuid('user_id')
      .notNull()
      .references(() => users.id, { onDelete: 'cascade' }),
    rating: real('rating').notNull(),
    title: varchar('title', { length: 500 }).notNull(),
    content: text('content').notNull(),
    isVerified: boolean('is_verified').notNull().default(false),
    helpfulCount: integer('helpful_count').notNull().default(0),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index('reviews_course_idx').on(table.courseId),
    index('reviews_user_idx').on(table.userId),
    uniqueIndex('reviews_course_user_idx').on(table.courseId, table.userId),
  ],
);
