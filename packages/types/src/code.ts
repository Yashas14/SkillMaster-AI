// ════════════════════════════════════════════════════════════
// Code Execution types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601 } from './common';

export type SupportedLanguage = 'python' | 'javascript' | 'typescript';

export interface ExecuteCodeRequest {
  code: string;
  language: SupportedLanguage;
  stdin?: string;
  timeout?: number; // seconds
}

export interface ExecuteCodeResponse {
  stdout: string;
  stderr: string;
  exitCode: number;
  executionTime: number; // milliseconds
  memoryUsed?: number; // bytes
  timedOut: boolean;
}

export interface CodeReviewRequest {
  code: string;
  language: SupportedLanguage;
  reviewType: 'comprehensive' | 'security' | 'performance' | 'style' | 'bugs';
}

export interface CodeReviewResponse {
  id: UUID;
  overallScore: number;
  summary: string;
  issues: CodeReviewIssue[];
  suggestions: string[];
  reviewedAt: ISO8601;
}

export interface CodeReviewIssue {
  severity: 'info' | 'warning' | 'error' | 'critical';
  category: string;
  line?: number;
  message: string;
  suggestion?: string;
}

export interface CodeExplainRequest {
  code: string;
  language: SupportedLanguage;
  detail?: 'brief' | 'detailed' | 'line_by_line';
}

export interface CodeExplainResponse {
  explanation: string;
  concepts: string[];
  complexity: string;
}
