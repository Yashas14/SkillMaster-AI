// ════════════════════════════════════════════════════════════
// Database Schema - Users
// ════════════════════════════════════════════════════════════

import {
  pgTable,
  uuid,
  varchar,
  text,
  boolean,
  timestamp,
  jsonb,
  pgEnum,
  index,
  uniqueIndex,
} from 'drizzle-orm/pg-core';

export const userRoleEnum = pgEnum('user_role', [
  'student',
  'instructor',
  'admin',
  'super_admin',
]);

export const authProviderEnum = pgEnum('auth_provider', ['email', 'google', 'github']);

export const users = pgTable(
  'users',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    email: varchar('email', { length: 255 }).notNull().unique(),
    name: varchar('name', { length: 255 }).notNull(),
    displayName: varchar('display_name', { length: 255 }),
    passwordHash: text('password_hash'),
    avatarUrl: text('avatar_url'),
    role: userRoleEnum('role').notNull().default('student'),
    provider: authProviderEnum('provider').notNull().default('email'),
    providerId: varchar('provider_id', { length: 255 }),
    bio: text('bio'),
    headline: varchar('headline', { length: 500 }),
    website: text('website'),
    location: varchar('location', { length: 255 }),
    timezone: varchar('timezone', { length: 100 }).default('UTC'),
    language: varchar('language', { length: 10 }).default('en'),
    isVerified: boolean('is_verified').notNull().default(false),
    isActive: boolean('is_active').notNull().default(true),
    onboardingCompleted: boolean('onboarding_completed').notNull().default(false),
    lastLoginAt: timestamp('last_login_at', { withTimezone: true }),
    preferences: jsonb('preferences')
      .notNull()
      .default({
        theme: 'system',
        emailNotifications: true,
        pushNotifications: true,
        weeklyDigest: true,
        learningReminders: true,
        language: 'en',
        accessibility: {
          reducedMotion: false,
          highContrast: false,
          fontSize: 'medium',
          screenReader: false,
          captions: false,
        },
      }),
    profile: jsonb('profile')
      .notNull()
      .default({
        skills: [],
        interests: [],
        learningGoals: [],
        experienceLevel: 'beginner',
      }),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
    deletedAt: timestamp('deleted_at', { withTimezone: true }),
  },
  (table) => [
    uniqueIndex('users_email_idx').on(table.email),
    index('users_role_idx').on(table.role),
    index('users_provider_idx').on(table.provider),
    index('users_created_at_idx').on(table.createdAt),
  ],
);

export const userStats = pgTable('user_stats', {
  userId: uuid('user_id')
    .primaryKey()
    .references(() => users.id, { onDelete: 'cascade' }),
  totalCoursesEnrolled: varchar('total_courses_enrolled').notNull().default('0'),
  totalCoursesCompleted: varchar('total_courses_completed').notNull().default('0'),
  totalXp: varchar('total_xp').notNull().default('0'),
  currentLevel: varchar('current_level').notNull().default('1'),
  studyStreak: varchar('study_streak').notNull().default('0'),
  longestStreak: varchar('longest_streak').notNull().default('0'),
  totalStudyMinutes: varchar('total_study_minutes').notNull().default('0'),
  badgesEarned: varchar('badges_earned').notNull().default('0'),
  certificatesEarned: varchar('certificates_earned').notNull().default('0'),
  averageQuizScore: varchar('average_quiz_score').notNull().default('0'),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
});
