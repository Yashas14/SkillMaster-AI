// ════════════════════════════════════════════════════════════
// AI-related types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601 } from './common';

export enum AIModel {
  CLAUDE_OPUS = 'claude-opus-4-6',
  GPT_4O = 'gpt-4o',
  GEMINI_PRO = 'gemini-2.5-pro',
}

export enum TutorPersona {
  SOCRATIC_GUIDE = 'socratic_guide',
  STRICT_PROFESSOR = 'strict_professor',
  FRIENDLY_PEER = 'friendly_peer',
  DEBATE_PARTNER = 'debate_partner',
}

export interface ChatMessage {
  id: UUID;
  sessionId: UUID;
  role: 'user' | 'assistant' | 'system';
  content: string;
  contentType: 'text' | 'code' | 'diagram' | 'equation' | 'mixed';
  metadata?: ChatMessageMetadata;
  createdAt: ISO8601;
}

export interface ChatMessageMetadata {
  model?: AIModel;
  tokensUsed?: number;
  latencyMs?: number;
  codeBlocks?: CodeBlock[];
  equations?: string[];
  citations?: Citation[];
  persona?: TutorPersona;
}

export interface CodeBlock {
  language: string;
  code: string;
  filename?: string;
}

export interface Citation {
  source: string;
  title: string;
  url?: string;
  relevanceScore: number;
}

export interface ChatSession {
  id: UUID;
  userId: UUID;
  courseId?: UUID;
  lessonId?: UUID;
  title: string;
  persona: TutorPersona;
  messages: ChatMessage[];
  summary?: string;
  isActive: boolean;
  createdAt: ISO8601;
  updatedAt: ISO8601;
}

export interface TutorChatRequest {
  message: string;
  sessionId?: UUID;
  courseId?: UUID;
  lessonId?: UUID;
  persona?: TutorPersona;
  includeCode?: boolean;
  includeEquations?: boolean;
  context?: string;
}

export interface TutorChatResponse {
  sessionId: UUID;
  message: ChatMessage;
  suggestedFollowUps?: string[];
  relatedTopics?: string[];
}

export interface StreamChunk {
  type: 'text' | 'code_start' | 'code_content' | 'code_end' | 'equation' | 'done' | 'error';
  content: string;
  metadata?: Record<string, unknown>;
}

export interface AICodeReview {
  id: UUID;
  userId: UUID;
  code: string;
  language: string;
  correctness: ReviewSection;
  style: ReviewSection;
  complexity: ReviewSection;
  security: ReviewSection;
  suggestions: CodeSuggestion[];
  overallScore: number;
  summary: string;
  createdAt: ISO8601;
}

export interface ReviewSection {
  score: number;
  maxScore: number;
  issues: ReviewIssue[];
}

export interface ReviewIssue {
  severity: 'info' | 'warning' | 'error' | 'critical';
  line?: number;
  message: string;
  suggestion?: string;
}

export interface CodeSuggestion {
  type: 'refactor' | 'optimization' | 'best_practice' | 'security';
  description: string;
  originalCode: string;
  suggestedCode: string;
  explanation: string;
}

export interface RAGDocument {
  id: UUID;
  courseId: UUID;
  title: string;
  content: string;
  chunkIndex: number;
  totalChunks: number;
  embedding?: number[];
  metadata: {
    source: string;
    pageNumber?: number;
    section?: string;
    contentType: string;
  };
  createdAt: ISO8601;
}

export interface SearchQuery {
  query: string;
  filters?: {
    courseId?: UUID;
    contentType?: string;
    difficulty?: string;
    language?: string;
  };
  limit?: number;
  offset?: number;
  useRAG?: boolean;
}

export interface SearchResult {
  id: UUID;
  title: string;
  content: string;
  score: number;
  source: string;
  courseId?: UUID;
  lessonId?: UUID;
  highlights: string[];
  metadata: Record<string, unknown>;
}
