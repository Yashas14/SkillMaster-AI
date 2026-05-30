'use client';

import { useState } from 'react';

const RARITY_COLORS: Record<string, string> = {
  common: 'border-gray-300 bg-gray-50 dark:border-gray-700 dark:bg-gray-900',
  uncommon: 'border-green-400 bg-green-50 dark:border-green-700 dark:bg-green-950',
  rare: 'border-blue-400 bg-blue-50 dark:border-blue-700 dark:bg-blue-950',
  epic: 'border-purple-400 bg-purple-50 dark:border-purple-700 dark:bg-purple-950',
  legendary: 'border-yellow-400 bg-yellow-50 dark:border-yellow-700 dark:bg-yellow-950',
};

const BADGES = [
  { id: '1', name: 'First Steps', description: 'Complete your first lesson', icon: '👣', category: 'milestone', rarity: 'common', earned: true, earnedAt: '2024-01-15' },
  { id: '2', name: 'Quick Learner', description: 'Complete 10 lessons', icon: '⚡', category: 'milestone', rarity: 'common', earned: true, earnedAt: '2024-02-01' },
  { id: '3', name: 'Course Conqueror', description: 'Complete your first course', icon: '🏆', category: 'achievement', rarity: 'common', earned: true, earnedAt: '2024-03-10' },
  { id: '4', name: 'Quiz Ace', description: 'Score 100% on a quiz', icon: '🎯', category: 'quiz', rarity: 'uncommon', earned: true, earnedAt: '2024-02-20' },
  { id: '5', name: 'Week Warrior', description: 'Maintain a 7-day streak', icon: '🔥', category: 'streak', rarity: 'common', earned: true, earnedAt: '2024-03-01' },
  { id: '6', name: 'Knowledge Seeker', description: 'Complete 50 lessons', icon: '📖', category: 'milestone', rarity: 'uncommon', earned: false },
  { id: '7', name: 'Scholar', description: 'Complete 100 lessons', icon: '🎓', category: 'milestone', rarity: 'rare', earned: false },
  { id: '8', name: 'Month Master', description: 'Maintain a 30-day streak', icon: '🔥', category: 'streak', rarity: 'rare', earned: false },
  { id: '9', name: 'Polymath', description: 'Complete 5 courses', icon: '⭐', category: 'achievement', rarity: 'uncommon', earned: false },
  { id: '10', name: 'Code Warrior', description: 'Submit 50 code solutions', icon: '💻', category: 'coding', rarity: 'uncommon', earned: false },
  { id: '11', name: 'Master Learner', description: 'Complete 10 courses', icon: '👑', category: 'achievement', rarity: 'rare', earned: false },
  { id: '12', name: 'Legendary', description: 'Reach level 30', icon: '✨', category: 'milestone', rarity: 'legendary', earned: false },
];

const LEADERBOARD = [
  { rank: 1, name: 'Alex Chen', xp: 12500, level: 15, streak: 45, avatar: null },
  { rank: 2, name: 'Sarah Kim', xp: 11200, level: 14, streak: 30, avatar: null },
  { rank: 3, name: 'Mike Johnson', xp: 9800, level: 12, streak: 22, avatar: null },
  { rank: 4, name: 'Emily Davis', xp: 8500, level: 11, streak: 18, avatar: null },
  { rank: 5, name: 'You', xp: 2450, level: 8, streak: 12, avatar: null, isYou: true },
];

export default function LeaderboardPage() {
  const [tab, setTab] = useState<'badges' | 'leaderboard'>('badges');
  const [filter, setFilter] = useState<string>('all');

  const filteredBadges = filter === 'all'
    ? BADGES
    : filter === 'earned'
      ? BADGES.filter((b) => b.earned)
      : BADGES.filter((b) => b.category === filter);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Achievements</h1>
        <p className="text-muted-foreground">Badges, XP, and leaderboard</p>
      </div>

      {/* Profile Summary */}
      <div className="flex flex-wrap items-center gap-6 rounded-xl border bg-gradient-to-r from-blue-600 to-purple-600 p-6 text-white">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/20 text-2xl font-bold">
          8
        </div>
        <div>
          <p className="text-sm text-white/80">Level 8</p>
          <p className="text-2xl font-bold">2,450 XP</p>
          <div className="mt-1 h-2 w-48 rounded-full bg-white/20">
            <div className="h-2 rounded-full bg-white" style={{ width: '47%' }} />
          </div>
          <p className="mt-1 text-xs text-white/70">2,750 XP to Level 9</p>
        </div>
        <div className="ml-auto flex gap-8 text-center">
          <div>
            <p className="text-2xl font-bold">12</p>
            <p className="text-xs text-white/80">Day Streak</p>
          </div>
          <div>
            <p className="text-2xl font-bold">5</p>
            <p className="text-xs text-white/80">Badges</p>
          </div>
          <div>
            <p className="text-2xl font-bold">#5</p>
            <p className="text-xs text-white/80">Rank</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg border p-1">
        <button
          onClick={() => setTab('badges')}
          className={`flex-1 rounded-md py-2 text-sm font-medium transition-colors ${
            tab === 'badges' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Badges
        </button>
        <button
          onClick={() => setTab('leaderboard')}
          className={`flex-1 rounded-md py-2 text-sm font-medium transition-colors ${
            tab === 'leaderboard' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Leaderboard
        </button>
      </div>

      {tab === 'badges' ? (
        <>
          {/* Badge Filters */}
          <div className="flex flex-wrap gap-2">
            {['all', 'earned', 'milestone', 'achievement', 'quiz', 'streak', 'coding'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`rounded-full px-3 py-1 text-sm capitalize transition-colors ${
                  filter === f
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:text-foreground'
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          {/* Badge Grid */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {filteredBadges.map((badge) => (
              <div
                key={badge.id}
                className={`relative rounded-xl border-2 p-5 transition-all ${
                  RARITY_COLORS[badge.rarity]
                } ${badge.earned ? '' : 'opacity-50 grayscale'}`}
              >
                <div className="mb-3 text-4xl">{badge.icon}</div>
                <h3 className="font-semibold">{badge.name}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{badge.description}</p>
                <div className="mt-3 flex items-center justify-between">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${
                    badge.rarity === 'legendary' ? 'bg-yellow-200 text-yellow-800' :
                    badge.rarity === 'rare' ? 'bg-blue-200 text-blue-800' :
                    badge.rarity === 'uncommon' ? 'bg-green-200 text-green-800' :
                    'bg-gray-200 text-gray-800'
                  }`}>
                    {badge.rarity}
                  </span>
                  {badge.earned && (
                    <span className="text-xs text-muted-foreground">{badge.earnedAt}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      ) : (
        /* Leaderboard Table */
        <div className="rounded-xl border">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left text-sm font-medium">Rank</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Student</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">XP</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">Level</th>
                  <th className="px-4 py-3 text-right text-sm font-medium">Streak</th>
                </tr>
              </thead>
              <tbody>
                {LEADERBOARD.map((entry) => (
                  <tr
                    key={entry.rank}
                    className={`border-b transition-colors ${
                      (entry as any).isYou ? 'bg-blue-50 dark:bg-blue-950' : 'hover:bg-muted/50'
                    }`}
                  >
                    <td className="px-4 py-3">
                      <span className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-sm font-bold ${
                        entry.rank === 1 ? 'bg-yellow-100 text-yellow-700' :
                        entry.rank === 2 ? 'bg-gray-100 text-gray-700' :
                        entry.rank === 3 ? 'bg-orange-100 text-orange-700' :
                        'text-muted-foreground'
                      }`}>
                        {entry.rank}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-medium">
                          {entry.name[0]}
                        </div>
                        <span className="font-medium">{entry.name}</span>
                        {(entry as any).isYou && (
                          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                            You
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right font-medium">
                      {entry.xp.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right">{entry.level}</td>
                    <td className="px-4 py-3 text-right">{entry.streak} days</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
