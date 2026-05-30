<div align="center">

# 🎓 SkillMaster AI

### AI-Native Learning Management System — Built for the Future of Education

<br/>

[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-F7DF1E?style=for-the-badge)](LICENSE)

<br/>

**A production-grade, full-stack learning platform** with AI tutoring, adaptive assessments, gamification, real-time code execution, and blockchain-verified credentials.

[Getting Started](#-getting-started) •
[Features](#-key-features) •
[Architecture](#-architecture) •
[API Reference](#-api-reference) •
[Testing](#-testing) •
[Contributing](#contributing)

</div>

---

## 📖 Overview

SkillMaster AI reimagines online education by embedding artificial intelligence at every layer of the learning experience. Rather than treating AI as a bolt-on feature, it is woven into course delivery, assessment, progress tracking, and personalization — creating an adaptive platform that evolves with each learner.

**What makes it different:**
- **AI Tutor with 4 Personas** — Socratic Guide, Friendly Peer, Strict Professor, Debate Partner — each with distinct pedagogical approaches
- **Bloom's Taxonomy Quizzes** — Adaptive assessments that calibrate difficulty based on learner performance across cognitive levels
- **RAG-Powered Search** — Semantic course discovery using vector embeddings + hybrid BM25/KNN retrieval
- **30-Level Gamification Engine** — XP, badges (15 types), daily streaks with freeze protection, competitive leaderboards
- **Sandboxed Code Execution** — Run Python/JavaScript/TypeScript in isolated containers with AI-powered code review

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client (Browser)                            │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Next.js 15 Frontend (React 19, App Router)              │
│         Port 3000  •  NextAuth v5  •  Zustand  •  TanStack Query   │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BFF Layer (Node.js Express)                             │
│         Port 4000  •  API Aggregation  •  Request Proxying          │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python 3.12)                           │
│         Port 8000  •  17 Routers  •  Async SQLAlchemy  •  JWT       │
└──────┬──────────┬──────────┬──────────┬──────────┬──────────────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐
│PostgreSQL││  Redis   ││ MongoDB  ││Elastic-  ││ Anthropic│
│   16     ││    7     ││    7     ││search 8  ││ Claude   │
│(primary) ││(cache)   ││(content) ││(vectors) ││  (AI)    │
└──────────┘└──────────┘└──────────┘└──────────┘└──────────┘
```

### Monorepo Structure

```
skillmaster-ai/
├── apps/
│   ├── web/              # Next.js 15 — App Router, React 19, TypeScript
│   ├── api/              # FastAPI — Python 3.12, SQLAlchemy async, Pydantic v2
│   └── bff/              # Express — API aggregation, rate limiting, proxying
├── packages/
│   ├── types/            # 15 shared TypeScript type modules (course, auth, ai, etc.)
│   ├── db/               # Drizzle ORM schemas + migrations
│   └── ui/               # Shared React component library
├── infrastructure/
│   └── docker/           # Prometheus/Grafana monitoring configs
├── docker-compose.yml    # One-command infrastructure deployment
├── turbo.json            # Turborepo build pipeline config
└── pnpm-workspace.yaml   # pnpm workspace definition
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|-----------|---------|
| Next.js 15.5 (App Router) | Server/client rendering, file-based routing, API routes |
| React 19 | UI library with concurrent features |
| TypeScript 5.7 | End-to-end type safety |
| Tailwind CSS 4 | Utility-first styling |
| Zustand | Lightweight state management |
| TanStack Query v5 | Server state, caching, optimistic updates |
| Recharts | Analytics data visualization |
| NextAuth.js v5 | Authentication (JWT strategy) |

### Backend
| Technology | Purpose |
|-----------|---------|
| FastAPI 0.115 | High-performance async API framework |
| Python 3.12 | Latest Python with performance improvements |
| SQLAlchemy 2.x (async) | ORM with connection pooling (pool_size=20) |
| Pydantic v2 | Request/response validation (40+ schemas) |
| python-jose | JWT token creation and validation |
| bcrypt | Secure password hashing |
| Anthropic SDK | Claude AI integration (tutor, quizzes, code review) |
| Ruff | Lightning-fast Python linting |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| PostgreSQL 16 | Primary relational database (17 tables) |
| Redis 7 | Session caching, rate limiting, pub/sub |
| MongoDB 7 | Flexible content storage |
| Elasticsearch 8.12 | Vector search, full-text search, analytics |
| Docker Compose | Container orchestration (8 services) |
| Turborepo 2.3 | Monorepo build system with caching |
| pnpm 9.15 | Fast, disk-efficient package manager |
| Prometheus + Grafana | Monitoring stack (opt-in profile) |

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | >= 20.x | Frontend + BFF runtime |
| pnpm | >= 9.15 | Package management |
| Docker + Compose | v2+ | Infrastructure services |
| Git | Latest | Version control |

### Quick Start (3 commands)

```bash
# 1. Clone and install
git clone https://github.com/Yashas14/SkillMaster_LMS.git
cd SkillMaster_LMS/skillmaster-ai
pnpm install

# 2. Start infrastructure (PostgreSQL, Redis, MongoDB, Elasticsearch, API, BFF)
docker compose up -d

# 3. Start the frontend
pnpm --filter @skillmaster/web dev
```

Open http://localhost:3000 — the platform is ready.

### Environment Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

| Variable | Description | Required |
|----------|-------------|:--------:|
| `JWT_SECRET_KEY` | JWT signing secret (`openssl rand -hex 32`) | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |
| `AUTH_SECRET` | NextAuth secret (`openssl rand -base64 32`) | ✅ |
| `ANTHROPIC_API_KEY` | Claude API key | For AI |
| `OPENAI_API_KEY` | OpenAI embeddings key | For search |
| `AUTH_GOOGLE_ID` / `AUTH_GOOGLE_SECRET` | Google OAuth | Optional |
| `AUTH_GITHUB_ID` / `AUTH_GITHUB_SECRET` | GitHub OAuth | Optional |

> **Note**: The app runs without AI keys — AI features gracefully degrade with informative error messages.

### Running Without Docker

```bash
# Ensure PostgreSQL and Redis are running locally

# Terminal 1 — API
cd apps/api && pip install -e . && uvicorn app.main:app --reload --port 8000

# Terminal 2 — BFF
cd apps/bff && pnpm dev

# Terminal 3 — Frontend
cd apps/web && pnpm dev
```

### Service Ports

| Service | URL | Notes |
|---------|-----|-------|
| Frontend | http://localhost:3000 | Next.js dev server |
| BFF | http://localhost:4000 | API aggregation layer |
| API | http://localhost:8000 | FastAPI backend |
| Swagger UI | http://localhost:8000/docs | Interactive API docs |
| ReDoc | http://localhost:8000/redoc | Alternative API docs |
| PostgreSQL | localhost:5433 | Remapped from 5432 |
| Redis | localhost:6380 | Remapped from 6379 |
| Elasticsearch | localhost:9200 | Vector + full-text search |
| MongoDB | localhost:27017 | Content storage |

---

## ✨ Key Features

### 🤖 AI-Powered Learning Engine

| Feature | Description | Technology |
|---------|-------------|-----------|
| **AI Tutor** | Real-time streaming chat with 4 distinct teaching personas | Anthropic Claude, SSE |
| **Adaptive Quizzes** | Bloom's taxonomy quiz generation calibrated to cognitive level | Claude + custom prompts |
| **Code Playground** | Sandboxed execution for Python/JS/TS with AI review | Docker isolation |
| **Learning Paths** | Personalized curriculum generation from goals + existing skills | Claude + course graph |
| **Semantic Search** | Hybrid KNN + BM25 retrieval over all course content | Elasticsearch + OpenAI embeddings |
| **Code Review** | AI-powered analysis with improvement suggestions | Claude structured output |

### 📊 Gamification & Analytics

- **30-Level Progression System** — XP earned from completing lessons, quizzes, streaks
- **15 Badge Types** — Achievement-based (First Course, Quiz Master, Night Owl, etc.)
- **Daily Streaks** — Streak tracking with configurable freeze protection
- **Platform Leaderboard** — Competitive rankings with weekly/monthly/all-time views
- **Student Analytics** — XP trends, category breakdown, weekly activity heatmap
- **Instructor Analytics** — Course performance, enrollment funnels, revenue metrics
- **Platform Analytics** — Admin-level overview of system health and engagement

### 🔐 Authentication & Security

- **Multi-Provider Auth** — Email/password + Google + GitHub OAuth via NextAuth.js v5
- **JWT Tokens** — Access (60min) + Refresh (30 days) token rotation
- **Role-Based Access** — Student, Instructor, Admin, Super Admin with granular permissions
- **Security Headers** — X-Content-Type-Options, X-Frame-Options, Referrer-Policy
- **Request Tracing** — Unique `X-Request-ID` header for every request
- **Performance Timing** — `X-Process-Time` header for monitoring
- **Input Validation** — Pydantic v2 strict schemas on all inputs

### 🏆 Course & Progress Management

- **Course CRUD** — Create, publish, categorize, tag with full-text search
- **Module/Lesson Hierarchy** — Ordered modules with lessons, each with duration + content type
- **Enrollment Lifecycle** — Enroll → Active → Completed with status management
- **Granular Progress** — Lesson-level completion tracking with auto-calculated course %
- **Reviews & Ratings** — Students rate courses; aggregated scores for discovery
- **Certificates** — Auto-issued on completion with unique verification numbers

---

## 📡 API Reference

The API serves 17 route groups under `/api/v1/`. Full interactive documentation is available at `/docs` (Swagger) or `/redoc`.

### Core CRUD

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/auth/register` | — | Register (student/instructor) |
| `POST` | `/auth/login` | — | Get access + refresh tokens |
| `POST` | `/auth/refresh` | 🔑 | Rotate refresh token |
| `GET` | `/auth/me` | 🔑 | Current user profile |
| `GET` | `/courses` | — | List courses (paginated, filterable) |
| `POST` | `/courses` | 🔑 | Create course (instructor+) |
| `GET` | `/courses/{id}` | — | Course detail with modules |
| `GET` | `/courses/slug/{slug}` | — | Lookup by URL-friendly slug |
| `PATCH` | `/courses/{id}` | 🔑 | Update course (owner/admin) |
| `DELETE` | `/courses/{id}` | 🔑 | Soft-delete course |
| `GET` | `/enrollments` | 🔑 | User's enrollments |
| `POST` | `/enrollments` | 🔑 | Enroll in course |
| `GET` | `/users` | 🔑 | List users (admin) |
| `GET` | `/users/{id}` | 🔑 | User by ID |

### AI & Intelligence

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/ai/tutor/chat` | 🔑 | Streaming AI tutor (SSE) |
| `GET` | `/ai/tutor/sessions` | 🔑 | Chat history |
| `POST` | `/quizzes/generate` | 🔑 | Generate adaptive quiz |
| `POST` | `/quizzes/{id}/submit` | 🔑 | Submit + auto-grade |
| `POST` | `/code/execute` | 🔑 | Run code in sandbox |
| `POST` | `/code/review` | 🔑 | AI code review |
| `POST` | `/code/explain` | 🔑 | AI code explanation |
| `POST` | `/learning-paths` | 🔑 | Generate learning path |
| `GET` | `/search/courses` | — | Full-text search |
| `POST` | `/search/semantic` | 🔑 | RAG semantic search |

### Gamification & Social

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/gamification/profile` | 🔑 | XP, level, badges, streaks |
| `GET` | `/gamification/leaderboard` | 🔑 | Platform rankings |
| `POST` | `/gamification/streak` | 🔑 | Record daily activity |
| `POST` | `/gamification/check-badges` | 🔑 | Check new badge eligibility |
| `GET` | `/analytics/student` | 🔑 | Learning analytics |
| `GET` | `/analytics/instructor` | 🔑 | Course analytics |
| `GET` | `/analytics/platform` | 🔑 | Admin metrics |
| `GET` | `/notifications` | 🔑 | User notifications |
| `POST` | `/notifications/read-all` | 🔑 | Mark all read |
| `POST` | `/certificates/issue/{id}` | 🔑 | Issue certificate |
| `GET` | `/certificates/verify/{num}` | — | Public verification |
| `GET` | `/reviews/course/{id}` | — | Course reviews |
| `POST` | `/reviews` | 🔑 | Submit review |

---

## 🧪 Testing

### Backend — 101 Tests (Pytest)

```bash
# Run all backend tests
docker exec skillmaster-api python -m pytest tests/ -v

# Or locally
cd apps/api && pip install -e ".[dev]" && pytest -v --cov=app

# Run specific module
pytest tests/test_auth.py -v
pytest tests/test_comprehensive.py -v
```

**Coverage includes:**
| Module | Tests | Covers |
|--------|:-----:|--------|
| Authentication | 12 | Register, login, refresh, JWT validation, role enforcement |
| Courses | 14 | CRUD, pagination, filters, slug lookup, authorization |
| Enrollments | 10 | Enroll, list, status updates, progress tracking |
| Progress | 6 | Lesson progress, course completion calculation |
| Users | 7 | CRUD, admin operations, profile updates |
| Middleware | 5 | Timing headers, security headers, request IDs |
| Advanced | 14 | Gamification, analytics, certificates, notifications |
| Comprehensive | 33 | All remaining endpoints (reviews, search, code, AI, etc.) |

### Frontend — 58 Tests (Vitest + Testing Library)

```bash
# Run all frontend tests
pnpm --filter @skillmaster/web vitest run

# Watch mode
pnpm --filter @skillmaster/web vitest

# Specific file
pnpm --filter @skillmaster/web vitest run src/lib/__tests__/utils.test.ts
```

**Coverage includes:**
| Module | Tests | Covers |
|--------|:-----:|--------|
| API Client | 12 | HTTP methods, auth headers, error handling, token refresh |
| Utilities | 22 | cn(), formatDuration, formatNumber, slugify, truncate, etc. |
| Stores | 12 | Auth store, course store, notification store (Zustand) |
| Components | 12 | Dashboard sidebar, header, search, theme toggle |

---

## 🗄️ Database Schema

17 tables powering the platform:

```
┌────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│     users      │────▶│   enrollments   │────▶│ lesson_progress  │
│                │     │                 │     │                  │
│ id, email,     │     │ user_id,        │     │ enrollment_id,   │
│ name, role,    │     │ course_id,      │     │ lesson_id,       │
│ hashed_pass    │     │ status,         │     │ completed,       │
└───────┬────────┘     │ progress_pct    │     │ time_spent       │
        │              └─────────────────┘     └──────────────────┘
        │
        │              ┌─────────────────┐     ┌──────────────────┐
        ├─────────────▶│  chat_sessions  │────▶│  chat_messages   │
        │              └─────────────────┘     └──────────────────┘
        │
        │              ┌─────────────────┐     ┌──────────────────┐
        ├─────────────▶│  learning_paths │────▶│learning_path_items│
        │              └─────────────────┘     └──────────────────┘
        │
        │              ┌─────────────────┐
        ├─────────────▶│   user_badges   │  (15 badge types)
        ├─────────────▶│    user_xp      │  (XP transactions)
        ├─────────────▶│  user_streaks   │  (daily streaks)
        ├─────────────▶│  notifications  │
        └─────────────▶│  certificates   │

┌────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│    courses     │────▶│ course_modules  │────▶│     lessons      │
│                │     └─────────────────┘     └──────────────────┘
│ title, slug,   │
│ category,      │     ┌─────────────────┐
│ price, status  │────▶│ course_reviews  │
└───────┬────────┘     └─────────────────┘
        │
        │              ┌─────────────────┐     ┌──────────────────┐
        └─────────────▶│    quizzes      │────▶│ quiz_questions   │
                       └─────────────────┘     └──────────────────┘
                                               ┌──────────────────┐
                                               │  quiz_attempts   │
                                               └──────────────────┘
```

---

## 📂 Project Structure (Detailed)

<details>
<summary><strong>Frontend (apps/web/)</strong></summary>

```
apps/web/src/
├── app/                        # Next.js App Router
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Landing page
│   ├── providers.tsx           # SessionProvider + QueryClientProvider
│   ├── globals.css             # Tailwind global styles
│   ├── api/                    # API routes (NextAuth, AI proxy)
│   ├── login/                  # Login page
│   ├── register/               # Registration page
│   └── dashboard/
│       ├── page.tsx            # Dashboard home (stats, activity)
│       ├── analytics/          # Learning analytics charts
│       ├── certificates/       # Certificate gallery
│       ├── courses/[id]/       # Course detail + lesson player
│       ├── leaderboard/        # Gamification leaderboard
│       ├── learning-paths/     # AI learning path viewer
│       ├── notifications/      # Notification center
│       ├── playground/         # Code execution + AI review
│       └── settings/           # Profile & preferences
├── components/
│   ├── ai-tutor/              # AI chat interface components
│   └── dashboard/             # Sidebar, header, navigation
├── lib/
│   ├── auth.ts                # NextAuth v5 configuration
│   ├── api-client.ts          # Typed HTTP client (BFF proxy)
│   ├── store.ts               # Zustand stores (auth, courses, UI)
│   └── utils.ts               # Utility functions (20+ helpers)
└── test/                      # Vitest setup + test utilities
```
</details>

<details>
<summary><strong>Backend (apps/api/)</strong></summary>

```
apps/api/
├── app/
│   ├── main.py                # FastAPI app factory + middleware stack
│   ├── config.py              # Pydantic Settings (all env vars)
│   ├── database.py            # Async engine + session factory
│   ├── models.py              # 17 SQLAlchemy models
│   ├── schemas.py             # 40+ Pydantic request/response schemas
│   ├── auth.py                # JWT utilities + password hashing
│   ├── middleware.py          # 4 custom middleware classes
│   ├── routers/               # 17 route modules
│   │   ├── auth.py            # Register, login, refresh, OAuth
│   │   ├── courses.py         # Course CRUD with pagination
│   │   ├── enrollments.py     # Enrollment lifecycle
│   │   ├── progress.py        # Lesson + course progress
│   │   ├── ai_tutor.py        # Streaming AI chat (SSE)
│   │   ├── quiz.py            # Quiz generation + grading
│   │   ├── code.py            # Sandbox execution + AI review
│   │   ├── learning_path.py   # AI curriculum generation
│   │   ├── search.py          # RAG pipeline + full-text
│   │   ├── gamification.py    # XP, badges, streaks, leaderboard
│   │   ├── analytics.py       # Student/instructor/platform stats
│   │   ├── certificates.py    # Issue + verify certificates
│   │   ├── notifications.py   # CRUD + bulk operations
│   │   ├── reviews.py         # Course ratings
│   │   ├── users.py           # User management (admin)
│   │   ├── websocket.py       # Real-time connections
│   │   └── health.py          # Health + dependency checks
│   └── services/              # Business logic layer
│       ├── rag.py             # RAGPipeline (ES vector search)
│       ├── quiz_generator.py  # Bloom's taxonomy engine
│       ├── code_executor.py   # Docker sandbox + AI review
│       ├── learning_path.py   # Personalization engine
│       ├── gamification.py    # XP/badge/streak calculations
│       └── websocket_manager.py # Connection pool + rooms
├── tests/                     # 101 pytest tests
└── pyproject.toml             # Dependencies + tool config
```
</details>

<details>
<summary><strong>Shared Packages</strong></summary>

```
packages/
├── types/src/                 # Shared TypeScript types
│   ├── auth.ts                # User, Session, JWT types
│   ├── course.ts              # Course, Module, Lesson types
│   ├── enrollment.ts          # Enrollment, Progress types
│   ├── ai.ts                  # AI Tutor, Chat types
│   ├── quiz.ts                # Quiz, Question, Attempt types
│   ├── code.ts                # Execution, Review types
│   ├── learning-path.ts       # Path, PathItem types
│   ├── analytics.ts           # Dashboard data types
│   ├── notification.ts        # Notification types
│   ├── certificate.ts         # Certificate types
│   ├── review.ts              # Review types
│   ├── progress.ts            # Progress tracking types
│   ├── user.ts                # User profile types
│   └── common.ts              # Shared utilities (Pagination, etc.)
├── db/                        # Drizzle ORM
│   └── src/schema/            # Database schema definitions
└── ui/                        # Component library
    └── src/components/        # Button, Card, Input, Badge, etc.
```
</details>

---

## 🧰 Development Commands

```bash
# ─── Infrastructure ──────────────────────────────────
docker compose up -d                  # Start all services
docker compose down                   # Stop all services
docker compose logs -f api            # Follow API logs
docker compose up -d --build api      # Rebuild API container

# ─── Frontend ────────────────────────────────────────
pnpm --filter @skillmaster/web dev    # Dev server (port 3000)
pnpm --filter @skillmaster/web build  # Production build
pnpm --filter @skillmaster/web vitest # Run tests (watch mode)

# ─── Backend ─────────────────────────────────────────
docker exec skillmaster-api python -m pytest tests/ -v   # Run tests
docker exec skillmaster-api ruff check app/ --fix        # Lint + fix

# ─── Monorepo ────────────────────────────────────────
pnpm dev                              # Start all apps
pnpm build                            # Build everything (Turborepo cached)
pnpm lint                             # Lint all packages
pnpm type-check                       # TypeScript strict check
```

---

## 🔒 Security Considerations

- **No secrets in source** — All credentials loaded from environment variables
- **JWT with short expiry** — 60-minute access tokens with 30-day refresh rotation
- **Password hashing** — bcrypt with automatic salt generation
- **Input validation** — Pydantic v2 strict mode on all request bodies
- **SQL injection prevention** — SQLAlchemy parameterized queries throughout
- **CORS configured** — Explicit origin allowlist (not wildcard)
- **Security headers** — Applied via custom middleware on every response
- **Role-based authorization** — Decorator-based permission checks per endpoint

---

## 🚢 Deployment

### Docker (Production)

```bash
# Build production images
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or build individual services
docker build -t skillmaster-api ./apps/api
docker build -t skillmaster-bff -f apps/bff/Dockerfile .
```

### Environment Checklist

- [ ] Set `JWT_SECRET_KEY` to a cryptographically random 256-bit value
- [ ] Set `AUTH_SECRET` for NextAuth.js
- [ ] Configure `DATABASE_URL` pointing to production PostgreSQL
- [ ] Configure `REDIS_URL` pointing to production Redis
- [ ] Set `ENVIRONMENT=production` and `DEBUG=false`
- [ ] Configure OAuth credentials (Google, GitHub) with production redirect URIs
- [ ] Set `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` for AI features
- [ ] Enable HTTPS/TLS termination at load balancer

---

## 📊 Performance

- **Async all the way** — FastAPI + async SQLAlchemy + async Redis client
- **Connection pooling** — PostgreSQL pool_size=20, max_overflow=10
- **Response caching** — Redis-backed cache with intelligent TTLs
- **Turborepo caching** — Build artifacts cached locally and remotely
- **Optimistic UI** — TanStack Query mutations with rollback
- **Code splitting** — Next.js App Router automatic route-level splitting

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Student | demo@skillmaster.ai | Demo@1234 |

> Register a new account via `/register` or use the demo account above.

---

## Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** with conventional commits: `git commit -m 'feat: add feature'`
4. **Push** to your fork: `git push origin feature/your-feature`
5. **Open** a Pull Request with a clear description

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ by [Yashas](https://github.com/Yashas14)**

</div>
