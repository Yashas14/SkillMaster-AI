// ════════════════════════════════════════════════════════════
// Quiz & Assessment types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601, BloomLevel, Difficulty } from './common';

export interface Quiz {
  id: UUID;
  courseId: UUID;
  lessonId?: UUID;
  title: string;
  description: string;
  difficulty: Difficulty;
  bloomLevel: BloomLevel;
  timeLimit?: number; // seconds
  passingScore: number;
  questionCount: number;
  questions: QuizQuestion[];
  isAdaptive: boolean;
  createdAt: ISO8601;
}

export interface QuizQuestion {
  id: UUID;
  quizId: UUID;
  questionText: string;
  questionType: 'multiple_choice' | 'true_false' | 'short_answer' | 'code';
  options?: QuizOption[];
  correctAnswer: string;
  explanation: string;
  bloomLevel: BloomLevel;
  points: number;
  orderIndex: number;
}

export interface QuizOption {
  id: string;
  text: string;
  isCorrect: boolean;
}

export interface QuizAttempt {
  id: UUID;
  quizId: UUID;
  userId: UUID;
  answers: QuizAnswer[];
  score: number;
  maxScore: number;
  percentage: number;
  passed: boolean;
  bloomAnalysis?: BloomAnalysis;
  recommendations?: string[];
  startedAt: ISO8601;
  completedAt: ISO8601;
}

export interface QuizAnswer {
  questionId: UUID;
  answer: string;
  isCorrect: boolean;
  timeSpent?: number; // seconds
}

export interface BloomAnalysis {
  remember: number;
  understand: number;
  apply: number;
  analyze: number;
  evaluate: number;
  create: number;
}

export interface GenerateQuizRequest {
  courseId: UUID;
  lessonId?: UUID;
  difficulty?: Difficulty;
  questionCount?: number;
}

export interface SubmitQuizRequest {
  quizId: UUID;
  answers: Record<string, string>; // questionId -> answer
}

export interface QuizResultResponse {
  attempt: QuizAttempt;
  feedback: string;
  bloomAnalysis: BloomAnalysis;
  recommendations: string[];
  nextDifficultyLevel: Difficulty;
}
