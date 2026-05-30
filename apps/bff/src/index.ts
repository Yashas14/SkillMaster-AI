// ════════════════════════════════════════════════════════════
// BFF (Backend for Frontend) Server
// Aggregates API calls, handles caching, rate limiting
// ════════════════════════════════════════════════════════════

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { createProxyMiddleware } from 'http-proxy-middleware';

const app = express();
const PORT = process.env.BFF_PORT || 4000;
const API_URL = process.env.API_URL || 'http://localhost:8000';

// ─── Middleware ────────────────────────────────────────────

app.use(helmet());
app.use(compression());
app.use(morgan('combined'));
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
}));
app.use(express.json({ limit: '10mb' }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later.' },
});
app.use('/api/', limiter);

// Stricter rate limit for AI endpoints
const aiLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 20,
  message: { error: 'AI request limit exceeded. Try again in a minute.' },
});
app.use('/api/v1/ai/', aiLimiter);

// ─── Health Check ─────────────────────────────────────────

app.get('/health', (_req, res) => {
  res.json({
    status: 'healthy',
    service: 'skillmaster-bff',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
  });
});

// ─── API Proxy ────────────────────────────────────────────
// Proxy all /api requests to the FastAPI backend

app.use(
  '/api',
  createProxyMiddleware({
    target: API_URL,
    changeOrigin: true,
    ws: true,
    on: {
      proxyReq: (proxyReq, req) => {
        // Forward auth headers
        const authHeader = req.headers.authorization;
        if (authHeader) {
          proxyReq.setHeader('Authorization', authHeader);
        }
      },
      error: (err, _req, res) => {
        console.error('Proxy error:', err.message);
        if ('writeHead' in res && typeof res.writeHead === 'function') {
          (res as express.Response).status(502).json({
            error: 'Backend service unavailable',
          });
        }
      },
    },
  }),
);

// ─── Aggregated Endpoints ─────────────────────────────────

app.get('/bff/dashboard', async (req, res) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    res.status(401).json({ error: 'Unauthorized' });
    return;
  }

  try {
    const headers = { Authorization: authHeader, 'Content-Type': 'application/json' };

    // Parallel requests to aggregate dashboard data
    const [enrollmentsRes, progressRes] = await Promise.all([
      fetch(`${API_URL}/api/v1/enrollments/?limit=5`, { headers }),
      fetch(`${API_URL}/api/v1/progress/course/summary`, { headers }).catch(() => null),
    ]);

    const enrollments = enrollmentsRes.ok ? await enrollmentsRes.json() : [];
    const progress = progressRes?.ok ? await progressRes.json() : {};

    res.json({
      enrollments,
      progress,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Dashboard aggregation error:', error);
    res.status(500).json({ error: 'Failed to load dashboard data' });
  }
});

app.get('/bff/course/:courseId/full', async (req, res) => {
  const { courseId } = req.params;
  const authHeader = req.headers.authorization;
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (authHeader) headers.Authorization = authHeader;

  try {
    const [courseRes, reviewsRes] = await Promise.all([
      fetch(`${API_URL}/api/v1/courses/${courseId}`, { headers }),
      fetch(`${API_URL}/api/v1/reviews/course/${courseId}?limit=10`, { headers }).catch(() => null),
    ]);

    if (!courseRes.ok) {
      res.status(courseRes.status).json({ error: 'Course not found' });
      return;
    }

    const course = await courseRes.json();
    const reviews = reviewsRes?.ok ? await reviewsRes.json() as { reviews?: unknown[] } : { reviews: [] };

    res.json({
      course,
      reviews: reviews.reviews || [],
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Course aggregation error:', error);
    res.status(500).json({ error: 'Failed to load course data' });
  }
});

// ─── Gamification Aggregated Endpoint ─────────────────────

app.get('/bff/gamification', async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    res.status(401).json({ error: 'Unauthorized' });
    return;
  }

  try {
    const headers = { Authorization: authHeader, 'Content-Type': 'application/json' };

    const [profileRes, leaderboardRes] = await Promise.all([
      fetch(`${API_URL}/api/v1/gamification/profile`, { headers }),
      fetch(`${API_URL}/api/v1/gamification/leaderboard?limit=10`, { headers }),
    ]);

    const profile = profileRes.ok ? await profileRes.json() : {};
    const leaderboard = leaderboardRes.ok ? await leaderboardRes.json() : [];

    res.json({
      profile,
      leaderboard,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Gamification aggregation error:', error);
    res.status(500).json({ error: 'Failed to load gamification data' });
  }
});

// ─── Analytics Aggregated Endpoint ────────────────────────

app.get('/bff/analytics', async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    res.status(401).json({ error: 'Unauthorized' });
    return;
  }

  try {
    const headers = { Authorization: authHeader, 'Content-Type': 'application/json' };

    const [analyticsRes, gamificationRes] = await Promise.all([
      fetch(`${API_URL}/api/v1/analytics/student`, { headers }),
      fetch(`${API_URL}/api/v1/gamification/profile`, { headers }),
    ]);

    const analytics = analyticsRes.ok ? await analyticsRes.json() : {};
    const gamification = gamificationRes.ok ? await gamificationRes.json() : {};

    res.json({
      analytics,
      gamification,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Analytics aggregation error:', error);
    res.status(500).json({ error: 'Failed to load analytics data' });
  }
});

// ─── Learning Path Aggregated Endpoint ────────────────────

app.get('/bff/learning-paths', async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    res.status(401).json({ error: 'Unauthorized' });
    return;
  }

  try {
    const headers = { Authorization: authHeader, 'Content-Type': 'application/json' };

    const [pathsRes, recommendationRes] = await Promise.all([
      fetch(`${API_URL}/api/v1/learning-paths/`, { headers }),
      fetch(`${API_URL}/api/v1/learning-paths/recommendations`, { headers }).catch(() => null),
    ]);

    const paths = pathsRes.ok ? await pathsRes.json() : [];
    const recommendations = recommendationRes?.ok
      ? await recommendationRes.json()
      : [];

    res.json({
      paths,
      recommendations,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Learning path aggregation error:', error);
    res.status(500).json({ error: 'Failed to load learning paths' });
  }
});

// ─── Notifications Aggregated Endpoint ────────────────────

app.get('/bff/notifications', async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    res.status(401).json({ error: 'Unauthorized' });
    return;
  }

  try {
    const headers = { Authorization: authHeader, 'Content-Type': 'application/json' };
    const notificationsRes = await fetch(
      `${API_URL}/api/v1/notifications/?unread_only=false&limit=50`,
      { headers },
    );
    const notifications = notificationsRes.ok
      ? await notificationsRes.json() as { notifications?: unknown[]; unread_count?: number }
      : { notifications: [], unread_count: 0 };

    res.json({
      notifications: notifications.notifications || [],
      unreadCount: notifications.unread_count || 0,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Notifications aggregation error:', error);
    res.status(500).json({ error: 'Failed to load notifications' });
  }
});

// ─── Start Server ─────────────────────────────────────────

app.listen(PORT, () => {
  console.log(`🚀 BFF server running on http://localhost:${PORT}`);
  console.log(`📡 Proxying API to ${API_URL}`);
  console.log(`🔒 Rate limit: 100 req/min (API), 20 req/min (AI)`);
});

export default app;
