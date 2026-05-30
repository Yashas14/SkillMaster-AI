// ════════════════════════════════════════════════════════════
// Certificate & Credential types
// ════════════════════════════════════════════════════════════

import type { UUID, ISO8601 } from './common';

export type CertificateStatus = 'issued' | 'revoked' | 'expired';

export interface Certificate {
  id: UUID;
  userId: UUID;
  courseId: UUID;
  certificateNumber: string;
  title: string;
  recipientName: string;
  courseTitle: string;
  issuedAt: ISO8601;
  status: CertificateStatus;
  completionPercentage: number;
  blockchain?: BlockchainCredential;
}

export interface BlockchainCredential {
  verified: boolean;
  txHash: string;
  network: string;
  tokenId?: string;
  contractAddress?: string;
  mintedAt: ISO8601;
}

export interface VerifyCertificateResponse {
  valid: boolean;
  certificate?: Certificate;
  message: string;
  blockchainVerified: boolean;
}

export interface MintCertificateRequest {
  certificateId: UUID;
  walletAddress: string;
}

export interface MintCertificateResponse {
  success: boolean;
  txHash: string;
  tokenId: string;
  network: string;
  explorerUrl: string;
}
