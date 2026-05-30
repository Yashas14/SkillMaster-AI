// ════════════════════════════════════════════════════════════
// Course types
// ════════════════════════════════════════════════════════════

import type {
  UUID,
  ISO8601,
  URL,
  SoftDeleteFields,
  Difficulty,
  BloomLevel,
  ContentType,
} from './common';

export enum CourseStatus {
  DRAFT = 'draft',
  REVIEW = 'review',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
}

export enum CourseCategory {
  PROGRAMMING = 'programming',
  DATA_SCIENCE = 'data_science',
  WEB_DEVELOPMENT = 'web_development',
  MOBILE_DEVELOPMENT = 'mobile_development',
  AI_ML = 'ai_ml',
  DEVOPS = 'devops',
  DESIGN = 'design',
  BUSINESS = 'business',
  SCIENCE = 'science',
  MATHEMATICS = 'mathematics',
  LANGUAGE = 'language',
  OTHER = 'other',
}

export interface Course extends SoftDeleteFields {
  id: UUID;
  title: string;
  slug: string;
  description: string;
  shortDescription: string;
  instructorId: UUID;
  thumbnailUrl?: URL;
  previewVideoUrl?: URL;
  category: CourseCategory;
  subcategory?: string;
  tags: string[];
  difficulty: Difficulty;
  language: string;
  status: CourseStatus;
  price: number;
  currency: string;
  isFree: boolean;
  estimatedDurationMinutes: number;
  totalLessons: number;
  totalModules: number;
  rating: number;
  totalRatings: number;
  totalEnrollments: number;
  prerequisites: string[];
  learningOutcomes: string[];
  targetAudience: string[];
  syllabus: CourseModule[];
  metadata: CourseMetadata;
  publishedAt?: ISO8601;
}

export interface CourseModule {
  id: UUID;
  courseId: UUID;
  title: string;
  description: string;
  order: number;
  estimatedDurationMinutes: number;
  lessons: Lesson[];
}

export interface Lesson {
  id: UUID;
  moduleId: UUID;
  title: string;
  description: string;
  contentType: ContentType;
  order: number;
  estimatedDurationMinutes: number;
  isFree: boolean;
  isRequired: boolean;
  bloomLevel: BloomLevel;
  content: LessonContent;
  resources: LessonResource[];
}

export interface LessonContent {
  videoUrl?: URL;
  videoDurationSeconds?: number;
  articleHtml?: string;
  articleMarkdown?: string;
  quizId?: UUID;
  assignmentId?: UUID;
  labId?: UUID;
  transcript?: string;
  captions?: Caption[];
}

export interface Caption {
  language: string;
  url: URL;
}

export interface LessonResource {
  id: UUID;
  title: string;
  type: 'pdf' | 'link' | 'code' | 'download';
  url: URL;
  size?: number;
}

export interface CourseMetadata {
  seoTitle?: string;
  seoDescription?: string;
  ogImage?: URL;
  structuredData?: Record<string, unknown>;
}

export interface CreateCourseInput {
  title: string;
  description: string;
  shortDescription: string;
  category: CourseCategory;
  subcategory?: string;
  tags?: string[];
  difficulty: Difficulty;
  language?: string;
  price?: number;
  currency?: string;
  prerequisites?: string[];
  learningOutcomes?: string[];
  targetAudience?: string[];
}

export interface UpdateCourseInput {
  title?: string;
  description?: string;
  shortDescription?: string;
  category?: CourseCategory;
  subcategory?: string;
  tags?: string[];
  difficulty?: Difficulty;
  language?: string;
  price?: number;
  status?: CourseStatus;
  thumbnailUrl?: URL;
  previewVideoUrl?: URL;
  prerequisites?: string[];
  learningOutcomes?: string[];
  targetAudience?: string[];
}

// CourseReview is defined in review.ts
export type { CourseReview } from './review';

export interface CourseFilter {
  category?: CourseCategory;
  difficulty?: Difficulty;
  priceMin?: number;
  priceMax?: number;
  rating?: number;
  language?: string;
  instructorId?: UUID;
  search?: string;
  tags?: string[];
  isFree?: boolean;
}
