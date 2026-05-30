// ════════════════════════════════════════════════════════════
// Learning Path types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601, Difficulty } from './common';

export type LearningPathStatus = 'active' | 'completed' | 'paused' | 'archived';
export type PathItemStatus = 'not_started' | 'in_progress' | 'completed' | 'skipped';
export type PathItemType = 'course' | 'lesson' | 'quiz' | 'project' | 'reading' | 'practice';

export interface LearningPath {
  id: UUID;
  userId: UUID;
  title: string;
  goal: string;
  currentSkills: string[];
  targetSkills: string[];
  status: LearningPathStatus;
  progress: number; // 0-100
  estimatedWeeks: number;
  weeklyHoursCommitment: number;
  items: LearningPathItem[];
  aiGenerated: boolean;
  createdAt: ISO8601;
  updatedAt: ISO8601;
}

export interface LearningPathItem {
  id: UUID;
  pathId: UUID;
  title: string;
  description: string;
  itemType: PathItemType;
  status: PathItemStatus;
  orderIndex: number;
  estimatedHours: number;
  courseId?: UUID;
  lessonId?: UUID;
  externalUrl?: string;
  difficulty?: Difficulty;
  completedAt?: ISO8601;
}

export interface CreateLearningPathRequest {
  goal: string;
  currentSkills: string[];
  targetSkills: string[];
  weeklyHoursCommitment: number;
  preferredDifficulty?: Difficulty;
}

export interface LearningPathRecommendation {
  pathId: UUID;
  nextAction: string;
  reason: string;
  suggestedCourseId?: UUID;
  suggestedLessonId?: UUID;
  estimatedTime: number;
}
