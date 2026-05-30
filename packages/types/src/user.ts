// ════════════════════════════════════════════════════════════
// User types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601, Email, URL, SoftDeleteFields } from './common';

export enum UserRole {
  STUDENT = 'student',
  INSTRUCTOR = 'instructor',
  ADMIN = 'admin',
  SUPER_ADMIN = 'super_admin',
}

export enum AuthProvider {
  EMAIL = 'email',
  GOOGLE = 'google',
  GITHUB = 'github',
}

export interface User extends SoftDeleteFields {
  id: UUID;
  email: Email;
  name: string;
  displayName?: string;
  avatarUrl?: URL;
  role: UserRole;
  provider: AuthProvider;
  providerId?: string;
  bio?: string;
  headline?: string;
  website?: URL;
  location?: string;
  timezone?: string;
  language: string;
  isVerified: boolean;
  isActive: boolean;
  lastLoginAt?: ISO8601;
  onboardingCompleted: boolean;
  preferences: UserPreferences;
  profile: UserProfile;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  emailNotifications: boolean;
  pushNotifications: boolean;
  weeklyDigest: boolean;
  learningReminders: boolean;
  reminderTime?: string;
  language: string;
  accessibility: AccessibilityPreferences;
}

export interface AccessibilityPreferences {
  reducedMotion: boolean;
  highContrast: boolean;
  fontSize: 'small' | 'medium' | 'large' | 'xlarge';
  screenReader: boolean;
  captions: boolean;
}

export interface UserProfile {
  education?: string;
  occupation?: string;
  company?: string;
  skills: string[];
  interests: string[];
  learningGoals: string[];
  experienceLevel: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  socialLinks?: SocialLinks;
}

export interface SocialLinks {
  linkedin?: URL;
  github?: URL;
  twitter?: URL;
  portfolio?: URL;
}

export interface UserStats {
  userId: UUID;
  totalCoursesEnrolled: number;
  totalCoursesCompleted: number;
  totalXp: number;
  currentLevel: number;
  studyStreak: number;
  longestStreak: number;
  totalStudyMinutes: number;
  badgesEarned: number;
  certificatesEarned: number;
  averageQuizScore: number;
}

export interface CreateUserInput {
  email: Email;
  name: string;
  password?: string;
  role?: UserRole;
  provider?: AuthProvider;
  providerId?: string;
  avatarUrl?: URL;
}

export interface UpdateUserInput {
  name?: string;
  displayName?: string;
  avatarUrl?: URL;
  bio?: string;
  headline?: string;
  website?: URL;
  location?: string;
  timezone?: string;
  language?: string;
  preferences?: Partial<UserPreferences>;
  profile?: Partial<UserProfile>;
}
