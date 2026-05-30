// ════════════════════════════════════════════════════════════
// Analytics types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601 } from './common';

export interface LearningAnalytics {
  userId: UUID;
  period: 'daily' | 'weekly' | 'monthly' | 'all_time';
  metrics: {
    studyTimeMinutes: number;
    lessonsCompleted: number;
    quizzesTaken: number;
    averageQuizScore: number;
    xpEarned: number;
    streakDays: number;
    conceptsMastered: number;
  };
  dailyActivity: DailyActivity[];
  skillRadar: SkillRadarData[];
  learningVelocity: VelocityDataPoint[];
}

export interface DailyActivity {
  date: ISO8601;
  studyMinutes: number;
  lessonsCompleted: number;
  xpEarned: number;
}

export interface SkillRadarData {
  skill: string;
  score: number;
  maxScore: number;
  peerAverage: number;
}

export interface VelocityDataPoint {
  week: string;
  conceptsMastered: number;
  target: number;
}

export interface InstructorAnalytics {
  instructorId: UUID;
  totalStudents: number;
  totalRevenue: number;
  totalCourses: number;
  averageRating: number;
  coursePerformance: CourseAnalytics[];
  revenueTimeline: RevenueDataPoint[];
  studentEngagement: EngagementMetrics;
}

export interface CourseAnalytics {
  courseId: UUID;
  courseTitle: string;
  enrollments: number;
  completionRate: number;
  averageRating: number;
  revenue: number;
  dropoffPoints: DropoffPoint[];
}

export interface DropoffPoint {
  lessonId: UUID;
  lessonTitle: string;
  position: number;
  dropoffRate: number;
}

export interface RevenueDataPoint {
  date: ISO8601;
  amount: number;
  enrollments: number;
}

export interface EngagementMetrics {
  averageWatchTime: number;
  averageCompletionRate: number;
  averageQuizScore: number;
  activeStudentsThisWeek: number;
  atRiskStudents: number;
}

export interface PlatformAnalytics {
  totalUsers: number;
  totalCourses: number;
  totalEnrollments: number;
  totalRevenue: number;
  monthlyActiveUsers: number;
  averageSessionDuration: number;
  topCourses: { courseId: UUID; title: string; enrollments: number }[];
  userGrowth: { date: ISO8601; count: number }[];
  revenueGrowth: RevenueDataPoint[];
}

export interface GamificationProfile {
  userId: UUID;
  xp: number;
  level: number;
  nextLevelXp: number;
  rank: number;
  badges: Badge[];
  achievements: Achievement[];
  streak: {
    current: number;
    longest: number;
    lastActivity: ISO8601;
  };
}

export interface Badge {
  id: UUID;
  name: string;
  description: string;
  iconUrl: string;
  category: string;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  earnedAt: ISO8601;
  isNFT: boolean;
  tokenId?: string;
}

export interface Achievement {
  id: UUID;
  name: string;
  description: string;
  progress: number;
  target: number;
  isCompleted: boolean;
  completedAt?: ISO8601;
  xpReward: number;
}

export interface LeaderboardEntry {
  rank: number;
  userId: UUID;
  userName: string;
  avatarUrl?: string;
  xp: number;
  level: number;
  streak: number;
  coursesCompleted: number;
}
