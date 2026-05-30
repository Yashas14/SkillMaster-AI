// ════════════════════════════════════════════════════════════
// Notification types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601 } from './common';

export type NotificationType =
  | 'achievement'
  | 'course'
  | 'certificate'
  | 'streak'
  | 'system'
  | 'review'
  | 'enrollment'
  | 'reminder';

export interface Notification {
  id: UUID;
  userId: UUID;
  type: NotificationType;
  title: string;
  message: string;
  read: boolean;
  actionUrl?: string;
  metadata?: Record<string, unknown>;
  createdAt: ISO8601;
}

export interface NotificationPreferences {
  email: boolean;
  push: boolean;
  weeklyDigest: boolean;
  learningReminders: boolean;
  achievementAlerts: boolean;
  courseUpdates: boolean;
}

export interface MarkNotificationsReadRequest {
  notificationIds: UUID[];
}
