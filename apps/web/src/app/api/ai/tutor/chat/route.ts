// ════════════════════════════════════════════════════════════
// AI Tutor Chat API Route (Next.js -> FastAPI proxy with SSE)
// ════════════════════════════════════════════════════════════

import { auth } from '@/lib/auth';
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const session = await auth();
  if (!session?.user) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401 });
  }

  const body = await request.json();

  try {
    const apiUrl = process.env.API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/v1/ai/tutor/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${(session as unknown as Record<string, unknown>).accessToken || ''}`,
      },
      body: JSON.stringify({
        ...body,
        user_id: session.user.id,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      return new Response(error, { status: response.status });
    }

    // Stream the response
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      },
    });
  } catch {
    return new Response(
      JSON.stringify({ error: 'Failed to connect to AI service' }),
      { status: 502 },
    );
  }
}
