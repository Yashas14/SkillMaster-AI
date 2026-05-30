'use client';

import { useState } from 'react';
import { useSession } from 'next-auth/react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

const COLORS = ['#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'];

export default function AnalyticsPage() {
  const { data: session } = useSession();
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  // In production, this would be fetched from /api/v1/analytics/student
  const analytics = {
    total_courses: 5,
    completed_courses: 2,
    total_lessons_completed: 48,
    total_study_hours: 32.5,
    average_quiz_score: 82.4,
    current_streak: 12,
    total_xp: 2450,
    level: 8,
    weekly_activity: [
      { date: 'Mon', xp: 120 }, { date: 'Tue', xp: 85 },
      { date: 'Wed', xp: 200 }, { date: 'Thu', xp: 150 },
      { date: 'Fri', xp: 90 }, { date: 'Sat', xp: 175 },
      { date: 'Sun', xp: 60 },
    ],
    category_breakdown: [
      { category: 'Programming', count: 3 },
      { category: 'Data Science', count: 1 },
      { category: 'Design', count: 1 },
    ],
    progress_over_time: [
      { month: 'Jan', lessons: 5 }, { month: 'Feb', lessons: 8 },
      { month: 'Mar', lessons: 12 }, { month: 'Apr', lessons: 10 },
      { month: 'May', lessons: 15 }, { month: 'Jun', lessons: 18 },
    ],
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">Track your learning journey</p>
        </div>
        <div className="flex gap-1 rounded-lg border p-1">
          {(['7d', '30d', '90d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                timeRange === range
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Courses Enrolled', value: analytics.total_courses, sub: `${analytics.completed_courses} completed` },
          { label: 'Study Hours', value: `${analytics.total_study_hours}h`, sub: 'Total time invested' },
          { label: 'Quiz Avg', value: `${analytics.average_quiz_score}%`, sub: 'Across all quizzes' },
          { label: 'XP Earned', value: analytics.total_xp.toLocaleString(), sub: `Level ${analytics.level}` },
        ].map((stat) => (
          <div key={stat.label} className="rounded-xl border bg-card p-5">
            <p className="text-sm text-muted-foreground">{stat.label}</p>
            <p className="mt-1 text-2xl font-bold">{stat.value}</p>
            <p className="mt-1 text-xs text-muted-foreground">{stat.sub}</p>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Weekly Activity */}
        <div className="rounded-xl border bg-card p-5">
          <h3 className="mb-4 font-semibold">Weekly XP Activity</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={analytics.weekly_activity}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
              />
              <Bar dataKey="xp" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Progress Over Time */}
        <div className="rounded-xl border bg-card p-5">
          <h3 className="mb-4 font-semibold">Lessons Completed</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={analytics.progress_over_time}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="month" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
              />
              <Line type="monotone" dataKey="lessons" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Category Breakdown */}
        <div className="rounded-xl border bg-card p-5">
          <h3 className="mb-4 font-semibold">Categories</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={analytics.category_breakdown}
                dataKey="count"
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={75}
                label={({ category, percent }) => `${category} ${(percent * 100).toFixed(0)}%`}
              >
                {analytics.category_breakdown.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Streak Info */}
        <div className="rounded-xl border bg-card p-5">
          <h3 className="mb-4 font-semibold">Learning Streak</h3>
          <div className="flex flex-col items-center gap-3">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-orange-400 to-red-500 text-white">
              <span className="text-2xl font-bold">{analytics.current_streak}</span>
            </div>
            <p className="text-sm text-muted-foreground">Day Streak</p>
            <div className="flex gap-1">
              {Array.from({ length: 7 }).map((_, i) => (
                <div
                  key={i}
                  className={`h-3 w-3 rounded-full ${
                    i < Math.min(analytics.current_streak, 7)
                      ? 'bg-orange-500'
                      : 'bg-muted'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Level Progress */}
        <div className="rounded-xl border bg-card p-5">
          <h3 className="mb-4 font-semibold">Level Progress</h3>
          <div className="flex flex-col items-center gap-3">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white">
              <span className="text-2xl font-bold">{analytics.level}</span>
            </div>
            <p className="text-sm text-muted-foreground">
              {analytics.total_xp.toLocaleString()} / 5,200 XP
            </p>
            <div className="h-2 w-full rounded-full bg-muted">
              <div
                className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-600"
                style={{ width: `${Math.min((analytics.total_xp / 5200) * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
