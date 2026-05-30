'use client';

import { useState } from 'react';

export default function CertificatesPage() {
  const certificates = [
    {
      id: '1',
      certificate_number: 'SM-A1B2-C3D4-E5F6',
      title: 'Certificate of Completion: Advanced React Patterns',
      course: 'Advanced React Patterns',
      issued_at: '2024-03-15',
      status: 'issued',
      blockchain_verified: true,
      blockchain_tx_hash: '0x1a2b3c4d...',
      blockchain_network: 'polygon-mumbai',
    },
    {
      id: '2',
      certificate_number: 'SM-G7H8-I9J0-K1L2',
      title: 'Certificate of Completion: Python for Data Science',
      course: 'Python for Data Science',
      issued_at: '2024-02-20',
      status: 'issued',
      blockchain_verified: false,
      blockchain_tx_hash: null,
      blockchain_network: null,
    },
  ];

  const [verifyInput, setVerifyInput] = useState('');
  const [verifyResult, setVerifyResult] = useState<{ valid: boolean; message: string; blockchain_verified: boolean } | null>(null);

  const handleVerify = async () => {
    // In production: GET /api/v1/certificates/verify/{cert_number}
    setVerifyResult({
      valid: true,
      message: 'Certificate is valid and verified.',
      blockchain_verified: true,
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Certificates</h1>
        <p className="text-muted-foreground">
          Blockchain-verifiable credentials for completed courses
        </p>
      </div>

      {/* Verify Section */}
      <div className="rounded-xl border bg-gradient-to-r from-blue-50 to-purple-50 p-6 dark:from-blue-950 dark:to-purple-950">
        <h2 className="font-semibold">Verify a Certificate</h2>
        <p className="text-sm text-muted-foreground">
          Enter a certificate number to verify its authenticity.
        </p>
        <div className="mt-3 flex gap-2">
          <input
            type="text"
            value={verifyInput}
            onChange={(e) => setVerifyInput(e.target.value)}
            placeholder="SM-XXXX-XXXX-XXXX"
            className="flex-1 rounded-lg border bg-background px-4 py-2 text-sm font-mono"
          />
          <button
            onClick={handleVerify}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
          >
            Verify
          </button>
        </div>
        {verifyResult && (
          <div className={`mt-3 rounded-lg p-3 text-sm ${
            verifyResult.valid
              ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
              : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          }`}>
            {verifyResult.valid ? '✓' : '✗'} {verifyResult.message}
            {verifyResult.blockchain_verified && (
              <span className="ml-2 rounded-full bg-blue-100 px-2 py-0.5 text-xs text-blue-700 dark:bg-blue-800 dark:text-blue-200">
                Blockchain Verified
              </span>
            )}
          </div>
        )}
      </div>

      {/* My Certificates */}
      <div className="grid gap-4 md:grid-cols-2">
        {certificates.map((cert) => (
          <div key={cert.id} className="rounded-xl border bg-card overflow-hidden">
            {/* Certificate Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
              <div className="flex items-center gap-2 text-sm text-white/80">
                <span>SkillMaster AI</span>
                {cert.blockchain_verified && (
                  <span className="rounded-full bg-white/20 px-2 py-0.5 text-xs">
                    ⛓ On-chain
                  </span>
                )}
              </div>
              <h3 className="mt-2 text-lg font-bold">{cert.title}</h3>
              <p className="mt-1 font-mono text-sm text-white/70">{cert.certificate_number}</p>
            </div>

            {/* Certificate Body */}
            <div className="p-5 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Issued</span>
                <span className="font-medium">{cert.issued_at}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Status</span>
                <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900 dark:text-green-300">
                  {cert.status}
                </span>
              </div>
              {cert.blockchain_tx_hash && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Network</span>
                  <span className="font-mono text-xs">{cert.blockchain_network}</span>
                </div>
              )}

              <div className="flex gap-2 pt-2">
                <button className="flex-1 rounded-lg border px-3 py-2 text-sm font-medium hover:bg-muted">
                  Download PDF
                </button>
                {!cert.blockchain_verified && (
                  <button className="flex-1 rounded-lg bg-purple-600 px-3 py-2 text-sm font-medium text-white hover:bg-purple-700">
                    Mint to Blockchain
                  </button>
                )}
                <button className="rounded-lg border px-3 py-2 text-sm hover:bg-muted">
                  Share
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
